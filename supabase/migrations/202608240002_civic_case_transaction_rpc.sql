-- Atomic civic case state + audit-event persistence boundary.
-- The RPC is intended for the server-side Supabase client only.

create or replace function public.append_civic_case_event(
    p_case_id text,
    p_access_policy_ref text,
    p_status text,
    p_event_id text,
    p_event_type text,
    p_occurred_at timestamptz,
    p_actor_ref text default null,
    p_source_channel text default null,
    p_notes text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
    if coalesce(trim(p_access_policy_ref), '') = '' then
        raise exception 'access policy reference is required';
    end if;

    update public.civic_cases
       set status = p_status,
           updated_at = now()
     where case_id = p_case_id
       and access_policy_ref = p_access_policy_ref;

    if not found then
        raise exception 'case not found or access policy mismatch';
    end if;

    insert into public.civic_case_events (
        event_id, case_id, event_type, occurred_at, actor_ref, source_channel, notes
    ) values (
        p_event_id, p_case_id, p_event_type, p_occurred_at, p_actor_ref, p_source_channel, p_notes
    );
exception
    when others then
        raise;
end;
$$;

revoke all on function public.append_civic_case_event(text, text, text, text, text, timestamptz, text, text, text) from public;
revoke all on function public.append_civic_case_event(text, text, text, text, text, timestamptz, text, text, text) from anon;
revoke all on function public.append_civic_case_event(text, text, text, text, text, timestamptz, text, text, text) from authenticated;
