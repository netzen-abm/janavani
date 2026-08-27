-- JANAVANI canonical case-workflow schema
-- Date: 2026-08-27
-- Purpose: durable relational foundation for Case/Evidence/Authority/Consent/Document/Submission.
-- This migration is intentionally additive. It does not migrate or delete legacy CSV/JSONL data.
-- RLS is enabled with no public policies; application access must be explicitly designed before production use.

create table if not exists public.cases (
    id text primary key,
    issue text not null,
    status text not null default 'open',
    facts jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_cases_status on public.cases(status);
create index if not exists idx_cases_created_at on public.cases(created_at desc);

create table if not exists public.authorities (
    authority_id text primary key,
    name text not null,
    authority_type text not null,
    organisation_id text,
    office_id text,
    jurisdiction jsonb not null default '{}'::jsonb,
    postal_addresses jsonb not null default '[]'::jsonb,
    contact_points jsonb not null default '[]'::jsonb,
    official_urls jsonb not null default '[]'::jsonb,
    source_refs jsonb not null default '[]'::jsonb,
    verification_status text not null default 'unverified',
    last_verified_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_authorities_verification on public.authorities(verification_status);
create index if not exists idx_authorities_office on public.authorities(office_id);

create table if not exists public.evidence (
    evidence_id text primary key,
    case_id text not null references public.cases(id) on delete restrict,
    kind text not null,
    title text not null,
    source text not null,
    status text not null default 'provided',
    content_ref text,
    captured_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    provenance jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_evidence_case on public.evidence(case_id);
create index if not exists idx_evidence_status on public.evidence(status);

create table if not exists public.consents (
    consent_id text primary key,
    subject_id text not null references public.cases(id) on delete restrict,
    capability_id text not null,
    purpose text not null,
    scope jsonb not null default '[]'::jsonb,
    data_categories jsonb not null default '[]'::jsonb,
    grant_type text not null default 'explicit',
    status text not null,
    policy_version text not null,
    source_channel text not null,
    granted_at timestamptz not null,
    expires_at timestamptz,
    revoked_at timestamptz,
    proof_ref text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_consents_subject on public.consents(subject_id);
create index if not exists idx_consents_capability on public.consents(capability_id);
create index if not exists idx_consents_status on public.consents(status);

create table if not exists public.documents (
    document_id text primary key,
    case_id text references public.cases(id) on delete restrict,
    document_type text not null,
    title text not null,
    language text not null default 'en',
    subject text,
    body text,
    from_party jsonb,
    to_party jsonb not null default '{}'::jsonb,
    cc_parties jsonb not null default '[]'::jsonb,
    references_json jsonb not null default '[]'::jsonb,
    enclosures jsonb not null default '[]'::jsonb,
    version integer not null default 1,
    status text not null default 'draft',
    artifact_ref text,
    content_hash text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_documents_case on public.documents(case_id);
create index if not exists idx_documents_status on public.documents(status);

create table if not exists public.submissions (
    submission_id text primary key,
    operation_id text not null unique,
    case_id text not null references public.cases(id) on delete restrict,
    destination_ref text not null,
    status text not null default 'created',
    consent_ref text references public.consents(consent_id) on delete restrict,
    authorization_ref text,
    payload_hash text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_submissions_case on public.submissions(case_id);
create index if not exists idx_submissions_status on public.submissions(status);

create table if not exists public.case_evidence_refs (
    case_id text not null references public.cases(id) on delete cascade,
    evidence_id text not null references public.evidence(evidence_id) on delete restrict,
    created_at timestamptz not null default now(),
    primary key (case_id, evidence_id)
);

create table if not exists public.case_authority_refs (
    case_id text not null references public.cases(id) on delete cascade,
    authority_id text not null references public.authorities(authority_id) on delete restrict,
    created_at timestamptz not null default now(),
    primary key (case_id, authority_id)
);

create table if not exists public.case_consent_refs (
    case_id text not null references public.cases(id) on delete cascade,
    consent_id text not null references public.consents(consent_id) on delete restrict,
    created_at timestamptz not null default now(),
    primary key (case_id, consent_id)
);

create table if not exists public.case_document_refs (
    case_id text not null references public.cases(id) on delete cascade,
    document_id text not null references public.documents(document_id) on delete restrict,
    created_at timestamptz not null default now(),
    primary key (case_id, document_id)
);

create table if not exists public.case_submission_refs (
    case_id text not null references public.cases(id) on delete cascade,
    submission_id text not null references public.submissions(submission_id) on delete restrict,
    created_at timestamptz not null default now(),
    primary key (case_id, submission_id)
);

create table if not exists public.case_events (
    event_id bigint generated always as identity primary key,
    case_id text not null references public.cases(id) on delete restrict,
    event_type text not null,
    actor text,
    event_data jsonb not null default '{}'::jsonb,
    occurred_at timestamptz not null default now()
);

create index if not exists idx_case_events_case_time on public.case_events(case_id, occurred_at desc);

create table if not exists public.delivery_events (
    delivery_event_id bigint generated always as identity primary key,
    submission_id text not null references public.submissions(submission_id) on delete restrict,
    status text not null,
    adapter_id text,
    reference text,
    reason text,
    occurred_at timestamptz not null default now()
);

create index if not exists idx_delivery_events_submission_time on public.delivery_events(submission_id, occurred_at desc);

-- Durable records must not be publicly readable through the anonymous API by default.
alter table public.cases enable row level security;
alter table public.authorities enable row level security;
alter table public.evidence enable row level security;
alter table public.consents enable row level security;
alter table public.documents enable row level security;
alter table public.submissions enable row level security;
alter table public.case_evidence_refs enable row level security;
alter table public.case_authority_refs enable row level security;
alter table public.case_consent_refs enable row level security;
alter table public.case_document_refs enable row level security;
alter table public.case_submission_refs enable row level security;
alter table public.case_events enable row level security;
alter table public.delivery_events enable row level security;

comment on table public.cases is 'Canonical durable Janavani Case records; application workflow logic remains outside the database.';
comment on table public.evidence is 'Canonical evidence metadata; binary content is referenced externally.';
comment on table public.consents is 'Purpose-bound consent records; authorization enforcement remains in application/API policy.';
comment on table public.submissions is 'Canonical external-submission records; local persistence is not delivery confirmation.';
comment on table public.delivery_events is 'Append-only submission transport/delivery observations.';
