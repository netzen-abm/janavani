-- Atomic persistence boundary for canonical case workflow operations.
-- Application code may compose these functions as one database transaction.

create or replace function public.append_case_event_atomic(
    p_case_id text,
    p_event_type text,
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_events
language plpgsql
security invoker
as $$
declare
    v_event public.case_events;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;

    insert into public.case_events(case_id, event_type, actor, event_data)
    values (p_case_id, p_event_type, p_actor, coalesce(p_event_data, '{}'::jsonb))
    returning * into v_event;

    return v_event;
end;
$$;

create or replace function public.link_case_evidence_atomic(
    p_case_id text,
    p_evidence_id text,
    p_event_type text default 'case.evidence_linked',
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_evidence_refs
language plpgsql
security invoker
as $$
declare
    v_ref public.case_evidence_refs;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;
    if not exists (select 1 from public.evidence where evidence_id = p_evidence_id and case_id = p_case_id) then
        raise exception 'evidence does not belong to case: %', p_evidence_id;
    end if;

    insert into public.case_evidence_refs(case_id, evidence_id)
    values (p_case_id, p_evidence_id)
    on conflict (case_id, evidence_id) do update set case_id = excluded.case_id
    returning * into v_ref;

    perform public.append_case_event_atomic(p_case_id, p_event_type, p_actor, p_event_data || jsonb_build_object('evidence_id', p_evidence_id));
    return v_ref;
end;
$$;

create or replace function public.link_case_authority_atomic(
    p_case_id text,
    p_authority_id text,
    p_event_type text default 'case.authority_linked',
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_authority_refs
language plpgsql
security invoker
as $$
declare
    v_ref public.case_authority_refs;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;
    if not exists (select 1 from public.authorities where authority_id = p_authority_id) then
        raise exception 'authority not found: %', p_authority_id;
    end if;

    insert into public.case_authority_refs(case_id, authority_id)
    values (p_case_id, p_authority_id)
    on conflict (case_id, authority_id) do update set case_id = excluded.case_id
    returning * into v_ref;

    perform public.append_case_event_atomic(p_case_id, p_event_type, p_actor, p_event_data || jsonb_build_object('authority_id', p_authority_id));
    return v_ref;
end;
$$;

create or replace function public.link_case_consent_atomic(
    p_case_id text,
    p_consent_id text,
    p_event_type text default 'case.consent_linked',
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_consent_refs
language plpgsql
security invoker
as $$
declare
    v_ref public.case_consent_refs;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;
    if not exists (select 1 from public.consents where consent_id = p_consent_id and subject_id = p_case_id) then
        raise exception 'consent does not belong to case: %', p_consent_id;
    end if;

    insert into public.case_consent_refs(case_id, consent_id)
    values (p_case_id, p_consent_id)
    on conflict (case_id, consent_id) do update set case_id = excluded.case_id
    returning * into v_ref;

    perform public.append_case_event_atomic(p_case_id, p_event_type, p_actor, p_event_data || jsonb_build_object('consent_id', p_consent_id));
    return v_ref;
end;
$$;

create or replace function public.link_case_document_atomic(
    p_case_id text,
    p_document_id text,
    p_event_type text default 'case.document_linked',
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_document_refs
language plpgsql
security invoker
as $$
declare
    v_ref public.case_document_refs;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;
    if not exists (select 1 from public.documents where document_id = p_document_id and case_id = p_case_id) then
        raise exception 'document does not belong to case: %', p_document_id;
    end if;

    insert into public.case_document_refs(case_id, document_id)
    values (p_case_id, p_document_id)
    on conflict (case_id, document_id) do update set case_id = excluded.case_id
    returning * into v_ref;

    perform public.append_case_event_atomic(p_case_id, p_event_type, p_actor, p_event_data || jsonb_build_object('document_id', p_document_id));
    return v_ref;
end;
$$;

create or replace function public.link_case_submission_atomic(
    p_case_id text,
    p_submission_id text,
    p_event_type text default 'case.submission_linked',
    p_actor text default null,
    p_event_data jsonb default '{}'::jsonb
) returns public.case_submission_refs
language plpgsql
security invoker
as $$
declare
    v_ref public.case_submission_refs;
begin
    if not exists (select 1 from public.cases where id = p_case_id) then
        raise exception 'case not found: %', p_case_id;
    end if;
    if not exists (select 1 from public.submissions where submission_id = p_submission_id and case_id = p_case_id) then
        raise exception 'submission does not belong to case: %', p_submission_id;
    end if;

    insert into public.case_submission_refs(case_id, submission_id)
    values (p_case_id, p_submission_id)
    on conflict (case_id, submission_id) do update set case_id = excluded.case_id
    returning * into v_ref;

    perform public.append_case_event_atomic(p_case_id, p_event_type, p_actor, p_event_data || jsonb_build_object('submission_id', p_submission_id));
    return v_ref;
end;
$$;

revoke all on function public.append_case_event_atomic(text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_evidence_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_authority_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_consent_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_document_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_submission_atomic(text, text, text, text, jsonb) from public, anon, authenticated;

comment on function public.append_case_event_atomic(text, text, text, jsonb) is 'Privileged atomic append-only Case event operation; application/RLS policy must explicitly grant execution.';
