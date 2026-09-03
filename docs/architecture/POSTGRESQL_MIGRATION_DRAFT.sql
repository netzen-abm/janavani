-- Janavani — PostgreSQL Civic Case migration DRAFT
-- STATUS: REVIEW ONLY / NOT AUTHORIZED FOR PRODUCTION EXECUTION
-- This draft intentionally excludes RLS policies, legacy-data migration,
-- destructive changes, triggers containing business workflow logic, and
-- production-specific Supabase configuration.

create table if not exists civic_cases (
    case_id text primary key,
    case_type text not null,
    subject text not null,
    narrative text not null,
    created_by text,
    jurisdiction_json jsonb not null default '{}'::jsonb,
    related_organisation_id text,
    related_office_id text,
    related_official_id text,
    related_representative_id text,
    subject_claims_json jsonb not null default '[]'::jsonb,
    status text not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    version bigint not null default 1,
    constraint civic_cases_version_positive check (version > 0),
    constraint civic_cases_subject_nonempty check (length(trim(subject)) > 0),
    constraint civic_cases_narrative_nonempty check (length(trim(narrative)) > 0)
);

create table if not exists civic_case_events (
    event_id text primary key,
    case_id text not null references civic_cases(case_id),
    event_type text not null,
    occurred_at timestamptz not null,
    actor_id text,
    source_channel text,
    source_ref text,
    notes text,
    metadata_json jsonb,
    event_version integer not null default 1,
    created_at timestamptz not null
);

create table if not exists civic_case_consents (
    consent_id text primary key,
    case_id text not null references civic_cases(case_id),
    purpose text not null,
    scope jsonb not null,
    grant_type text,
    status text not null,
    granted_by text,
    created_at timestamptz not null,
    expires_at timestamptz,
    revoked_at timestamptz,
    proof_ref text
);

create table if not exists civic_case_evidence_refs (
    case_id text not null references civic_cases(case_id),
    evidence_id text not null,
    relationship text not null,
    created_at timestamptz not null,
    created_by text,
    primary key (case_id, evidence_id, relationship)
);

create table if not exists civic_case_document_refs (
    case_id text not null references civic_cases(case_id),
    document_id text not null,
    relationship text not null,
    version bigint not null default 1,
    created_at timestamptz not null,
    primary key (case_id, document_id, relationship)
);

create table if not exists civic_case_submissions (
    submission_id text primary key,
    case_id text not null references civic_cases(case_id),
    destination_ref text not null,
    document_ref text,
    channel text not null,
    state text not null,
    attempted_at timestamptz,
    submitted_at timestamptz,
    acknowledged_at timestamptz,
    external_reference text,
    ack_ref text,
    error_code text,
    retry_count integer not null default 0,
    version bigint not null default 1,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    constraint civic_case_submissions_retry_nonnegative check (retry_count >= 0),
    constraint civic_case_submissions_version_positive check (version > 0)
);

create table if not exists civic_case_audit (
    audit_id text primary key,
    case_id text not null references civic_cases(case_id),
    actor_id text,
    action text not null,
    occurred_at timestamptz not null,
    result text not null,
    reason text,
    source_channel text,
    metadata_hash text
);

create index if not exists civic_cases_status_updated_idx
    on civic_cases(status, updated_at);

create index if not exists civic_cases_created_by_idx
    on civic_cases(created_by);

create index if not exists civic_case_events_case_occurred_idx
    on civic_case_events(case_id, occurred_at);

create index if not exists civic_case_submissions_case_attempted_idx
    on civic_case_submissions(case_id, attempted_at);

create index if not exists civic_case_submissions_destination_idx
    on civic_case_submissions(destination_ref);

create index if not exists civic_case_audit_case_occurred_idx
    on civic_case_audit(case_id, occurred_at);

-- IMPORTANT:
-- 1. Validate the actual Supabase/PostgreSQL environment before execution.
-- 2. Reconcile existing authority/document/evidence identities and FKs.
-- 3. Define RLS separately from this schema draft.
-- 4. Add canonical enum/value constraints only after runtime/canonical
--    reconciliation is formally verified.
-- 5. Test on a clean disposable database and against a restore before rollout.
-- 6. Do not run legacy CSV/JSONL migration as part of this draft.
