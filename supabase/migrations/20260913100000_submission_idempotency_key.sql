-- Janavani — additive submission idempotency migration.
-- STATUS: SCHEMA-ONLY / NOT A PRODUCTION ACTIVATION.
-- No RLS, legacy migration, or destructive change is introduced.

alter table if exists public.civic_case_submissions
    add column if not exists idempotency_key text;

update public.civic_case_submissions
set idempotency_key = submission_id
where idempotency_key is null;

alter table public.civic_case_submissions
    alter column idempotency_key set not null;

create unique index if not exists civic_case_submissions_idempotency_key_uidx
    on public.civic_case_submissions(idempotency_key);
