-- Janavani canonical Case + policy persistence schema.
-- Controlled migration: schema only. RLS is intentionally NOT enabled here.
-- Application/domain authorization remains authoritative until the RLS gate is separately approved.

create table if not exists public.civic_cases (
    case_id text primary key,
    case_type text not null,
    subject text not null check (btrim(subject) <> ''),
    narrative text not null check (btrim(narrative) <> ''),
    created_by text,
    jurisdiction jsonb not null,
    related_organisation_id text,
    related_office_id text,
    related_official_id text,
    related_representative_id text,
    claims jsonb not null default '[]'::jsonb,
    consent_refs jsonb not null default '[]'::jsonb,
    status text not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    version bigint not null default 1 check (version >= 1),
    check (created_at <= updated_at)
);

create table if not exists public.civic_case_events (
    event_id text primary key,
    case_id text not null references public.civic_cases(case_id),
    event_type text not null,
    occurred_at timestamptz not null,
    actor_id text,
    source_channel text,
    source_ref text,
    notes text,
    event_version integer not null,
    created_at timestamptz not null,
    metadata_hash text
);

create index if not exists civic_case_events_case_occurred_idx
    on public.civic_case_events(case_id, occurred_at);

create table if not exists public.civic_case_evidence_refs (
    case_id text not null references public.civic_cases(case_id),
    evidence_id text not null,
    relationship text not null,
    created_at timestamptz not null,
    created_by text not null,
    primary key (case_id, evidence_id, relationship)
);

create table if not exists public.civic_case_document_refs (
    case_id text not null references public.civic_cases(case_id),
    document_id text not null,
    relationship text not null,
    version integer not null check (version >= 1),
    created_at timestamptz not null,
    primary key (case_id, document_id, relationship, version)
);

create table if not exists public.civic_case_consents (
    consent_id text primary key,
    subject_id text not null,
    purpose text not null,
    scope jsonb not null,
    grant_type text not null,
    status text not null,
    created_at timestamptz not null,
    expires_at timestamptz,
    revoked_at timestamptz,
    proof_ref text
);

create index if not exists civic_case_consents_subject_idx
    on public.civic_case_consents(subject_id, created_at);

create table if not exists public.civic_case_submissions (
    submission_id text primary key,
    case_id text not null references public.civic_cases(case_id),
    destination_ref jsonb not null,
    transport text not null,
    status text not null,
    external_reference text,
    submitted_at timestamptz,
    acknowledged_at timestamptz,
    failure_reason text,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    version bigint not null default 1 check (version >= 1),
    check (created_at <= updated_at)
);

create index if not exists civic_case_submissions_case_status_idx
    on public.civic_case_submissions(case_id, status);

create index if not exists civic_cases_created_by_updated_idx
    on public.civic_cases(created_by, updated_at);
create index if not exists civic_cases_status_updated_idx
    on public.civic_cases(status, updated_at);
create index if not exists civic_cases_office_status_idx
    on public.civic_cases(related_office_id, status);
create index if not exists civic_cases_org_status_idx
    on public.civic_cases(related_organisation_id, status);

create table if not exists public.janavani_delegation_grants (
    delegation_id text primary key,
    grantor_id text not null,
    delegate_id text not null,
    capabilities jsonb not null,
    actions jsonb not null,
    resource_ids jsonb not null,
    expires_at timestamptz,
    revoked boolean not null default false
);

create index if not exists janavani_delegation_grants_delegate_idx
    on public.janavani_delegation_grants(delegate_id);

create table if not exists public.janavani_service_identity_policies (
    principal_id text primary key,
    allowed_capabilities jsonb not null,
    allowed_actions jsonb not null
);

-- RLS intentionally remains a separate security gate.
-- Do not add enable row level security or policy statements in this migration.
