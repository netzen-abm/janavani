-- Civic case persistence boundary.
-- Keep raw identity/evidence payloads out of this table; store references only.

create table if not exists public.civic_cases (
    case_id text primary key,
    case_type text not null,
    subject text not null,
    narrative text not null,
    created_by_ref text,
    related_office_id text,
    evidence_refs jsonb not null default '[]'::jsonb,
    document_refs jsonb not null default '[]'::jsonb,
    consent_refs jsonb not null default '[]'::jsonb,
    status text not null default 'draft',
    access_policy_ref text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint civic_cases_evidence_refs_array check (jsonb_typeof(evidence_refs) = 'array'),
    constraint civic_cases_document_refs_array check (jsonb_typeof(document_refs) = 'array'),
    constraint civic_cases_consent_refs_array check (jsonb_typeof(consent_refs) = 'array')
);

create table if not exists public.civic_case_events (
    event_id text primary key,
    case_id text not null references public.civic_cases(case_id) on delete cascade,
    event_type text not null,
    occurred_at timestamptz not null,
    actor_ref text,
    source_channel text,
    notes text
);

create index if not exists civic_cases_policy_idx on public.civic_cases(access_policy_ref);
create index if not exists civic_case_events_case_idx on public.civic_case_events(case_id, occurred_at);

alter table public.civic_cases enable row level security;
alter table public.civic_case_events enable row level security;

-- Application requests must set the policy reference in a trusted transaction context.
-- This is intentionally deny-by-default for ordinary client sessions.
create policy civic_cases_deny_direct_client_access
    on public.civic_cases
    for all
    to anon, authenticated
    using (false)
    with check (false);

create policy civic_case_events_deny_direct_client_access
    on public.civic_case_events
    for all
    to anon, authenticated
    using (false)
    with check (false);

comment on table public.civic_cases is 'Privacy-aware civic case metadata; raw identity and evidence bytes remain outside this table.';
comment on column public.civic_cases.access_policy_ref is 'Application authorization policy reference; not a bearer credential.';
