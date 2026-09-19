-- Janavani — Supabase Civic Case atomic-write boundary.
-- STATUS: REVIEW / NOT APPLIED TO LIVE SUPABASE.
-- This migration is intentionally server-side only. It does not enable RLS.
--
-- Prerequisites:
--   1. review identity/authorization matrix;
--   2. apply on a disposable database;
--   3. run negative-access and rollback tests;
--   4. only then apply to the live project.

alter table if exists public.civic_case_consents
    add column if not exists case_id text references public.civic_cases(case_id);

create index if not exists civic_case_consents_case_id_idx
    on public.civic_case_consents(case_id);

create or replace function public.janavani_persist_civic_case(
    p_case jsonb,
    p_expected_version bigint,
    p_events jsonb default '[]'::jsonb,
    p_evidence_refs jsonb default '[]'::jsonb,
    p_document_refs jsonb default '[]'::jsonb,
    p_actor_id text default null
)
returns jsonb
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
    v_case_id text := p_case->>'case_id';
    v_created_by text := p_case->>'created_by';
    v_current_version bigint;
    v_new_version bigint;
    v_created_at timestamptz;
    v_now timestamptz := clock_timestamp();
    v_event jsonb;
    v_ref jsonb;
begin
    if v_case_id is null or length(trim(v_case_id)) = 0 then
        raise exception 'case_id is required';
    end if;

    if p_actor_id is not null and v_created_by is not null
       and p_actor_id <> v_created_by then
        raise exception 'case actor does not match case owner';
    end if;

    select version, created_at
      into v_current_version, v_created_at
      from public.civic_cases
     where case_id = v_case_id
     for update;

    if not found then
        if p_expected_version is not null and p_expected_version <> 0 then
            raise exception 'expected version mismatch for new case';
        end if;

        insert into public.civic_cases (
            case_id, case_type, subject, narrative, created_by,
            jurisdiction, related_organisation_id, related_office_id,
            related_official_id, related_representative_id,
            claims, consent_refs, status, created_at, updated_at, version
        ) values (
            v_case_id,
            p_case->>'case_type',
            p_case->>'subject',
            p_case->>'narrative',
            v_created_by,
            coalesce(p_case->'jurisdiction', '{}'::jsonb),
            p_case->>'related_organisation_id',
            p_case->>'related_office_id',
            p_case->>'related_official_id',
            p_case->>'related_representative_id',
            coalesce(p_case->'claims', '[]'::jsonb),
            coalesce(p_case->'consent_refs', '[]'::jsonb),
            p_case->>'status',
            coalesce((p_case->>'created_at')::timestamptz, v_now),
            v_now,
            1
        );
        v_new_version := 1;
        v_created_at := coalesce((p_case->>'created_at')::timestamptz, v_now);
    else
        if p_expected_version is null or p_expected_version <> v_current_version then
            raise exception using
                errcode = '40001',
                message = format(
                    'stale Civic Case version: expected %s, found %s',
                    coalesce(p_expected_version::text, 'null'),
                    v_current_version
                );
        end if;

        v_new_version := v_current_version + 1;

        update public.civic_cases
           set case_type = p_case->>'case_type',
               subject = p_case->>'subject',
               narrative = p_case->>'narrative',
               created_by = v_created_by,
               jurisdiction = coalesce(p_case->'jurisdiction', '{}'::jsonb),
               related_organisation_id = p_case->>'related_organisation_id',
               related_office_id = p_case->>'related_office_id',
               related_official_id = p_case->>'related_official_id',
               related_representative_id = p_case->>'related_representative_id',
               claims = coalesce(p_case->'claims', '[]'::jsonb),
               consent_refs = coalesce(p_case->'consent_refs', '[]'::jsonb),
               status = p_case->>'status',
               updated_at = v_now,
               version = v_new_version
         where case_id = v_case_id
           and version = v_current_version;

        if not found then
            raise exception using
                errcode = '40001',
                message = 'stale Civic Case version';
        end if;
    end if;

    for v_event in select value from jsonb_array_elements(coalesce(p_events, '[]'::jsonb))
    loop
        insert into public.civic_case_events (
            event_id, case_id, event_type, occurred_at, actor_id,
            source_channel, source_ref, notes, event_version,
            created_at, metadata_hash
        ) values (
            v_event->>'event_id',
            v_case_id,
            v_event->>'event_type',
            coalesce((v_event->>'occurred_at')::timestamptz, v_now),
            v_event->>'actor_id',
            v_event->>'source_channel',
            v_event->>'source_ref',
            v_event->>'notes',
            coalesce((v_event->>'event_version')::integer, 1),
            v_now,
            v_event->>'metadata_hash'
        )
        on conflict (event_id) do nothing;
    end loop;

    for v_ref in select value from jsonb_array_elements(coalesce(p_evidence_refs, '[]'::jsonb))
    loop
        insert into public.civic_case_evidence_refs (
            case_id, evidence_id, relationship, created_at, created_by
        ) values (
            v_case_id,
            v_ref->>'evidence_id',
            coalesce(v_ref->>'relationship', 'case_evidence'),
            v_now,
            coalesce(v_ref->>'created_by', v_created_by)
        )
        on conflict (case_id, evidence_id, relationship) do nothing;
    end loop;

    for v_ref in select value from jsonb_array_elements(coalesce(p_document_refs, '[]'::jsonb))
    loop
        insert into public.civic_case_document_refs (
            case_id, document_id, relationship, version, created_at
        ) values (
            v_case_id,
            v_ref->>'document_id',
            coalesce(v_ref->>'relationship', 'case_document'),
            coalesce((v_ref->>'version')::integer, 1),
            v_now
        )
        on conflict (case_id, document_id, relationship) do nothing;
    end loop;

    return jsonb_build_object(
        'case_id', v_case_id,
        'version', v_new_version,
        'created_at', v_created_at,
        'updated_at', v_now
    );
end;
$$;

-- The function is not a client API. Keep execution server-side only.
revoke all on function public.janavani_persist_civic_case(
    jsonb, bigint, jsonb, jsonb, jsonb, text
) from public, anon, authenticated;

grant execute on function public.janavani_persist_civic_case(
    jsonb, bigint, jsonb, jsonb, jsonb, text
) to service_role;
