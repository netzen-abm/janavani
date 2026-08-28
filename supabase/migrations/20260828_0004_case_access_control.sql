-- Canonical principal-to-case authorization model.
--
-- The first RLS baseline deliberately denied all public API access because the
-- canonical schema had no durable principal/case relationship. This migration
-- introduces the minimum explicit relationship needed to write safe policies.
-- It does not grant broad access to any role.

create table if not exists public.case_access (
    case_id text not null references public.cases(id) on delete cascade,
    principal_id text not null,
    role text not null,
    created_at timestamptz not null default now(),
    primary key (case_id, principal_id),
    constraint case_access_role_check check (role in ('owner', 'collaborator', 'reviewer', 'submitter'))
);

create index if not exists idx_case_access_principal on public.case_access(principal_id);
create index if not exists idx_case_access_case_role on public.case_access(case_id, role);

alter table public.case_access enable row level security;
revoke all on table public.case_access from anon, authenticated;

-- Helper predicates remain SECURITY INVOKER so RLS is never bypassed by a
-- helper function. They are intended for use by explicitly granted policies.
create or replace function public.has_case_access(
    p_case_id text,
    p_principal_id text,
    p_roles text[] default array['owner','collaborator','reviewer','submitter']
) returns boolean
language sql
security invoker
stable
as $$
    select exists (
        select 1
        from public.case_access ca
        where ca.case_id = p_case_id
          and ca.principal_id = p_principal_id
          and ca.role = any(p_roles)
    );
$$;

revoke all on function public.has_case_access(text, text, text[]) from public, anon, authenticated;

comment on table public.case_access is 'Explicit principal-to-case authorization relation. principal_id must be bound to the authenticated identity by the API/authentication layer before policies are enabled.';
comment on function public.has_case_access(text, text, text[]) is 'Security-invoker case access predicate; not executable by public API roles until the principal binding and policy grant are approved.';
