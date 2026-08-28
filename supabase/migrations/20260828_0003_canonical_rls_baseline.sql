-- Canonical RLS baseline for Janavani durable case data.
--
-- This migration intentionally does NOT grant authenticated users broad access.
-- The current canonical application authorization model does not yet define a
-- database-backed principal-to-case membership relation. Until that relation
-- exists, allowing authenticated CRUD would be an unsafe privacy shortcut.
--
-- service_role/server-side administration may continue to operate through the
-- existing Supabase server boundary; this migration does not weaken RLS or
-- expose privileged RPCs to PostgREST clients.

-- RLS is the database safety net. Keep it enabled on every canonical durable table.
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

-- Explicitly prevent the public API roles from directly mutating or reading
-- canonical records. No policy is created to re-grant these operations yet.
revoke all on table public.cases from anon, authenticated;
revoke all on table public.authorities from anon, authenticated;
revoke all on table public.evidence from anon, authenticated;
revoke all on table public.consents from anon, authenticated;
revoke all on table public.documents from anon, authenticated;
revoke all on table public.submissions from anon, authenticated;
revoke all on table public.case_evidence_refs from anon, authenticated;
revoke all on table public.case_authority_refs from anon, authenticated;
revoke all on table public.case_consent_refs from anon, authenticated;
revoke all on table public.case_document_refs from anon, authenticated;
revoke all on table public.case_submission_refs from anon, authenticated;
revoke all on table public.case_events from anon, authenticated;
revoke all on table public.delivery_events from anon, authenticated;

-- Privileged atomic workflow functions remain explicitly non-public. Access
-- must be granted only to the trusted server execution role after integration
-- tests prove the application authorization path.
revoke all on function public.append_case_event_atomic(text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_evidence_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_authority_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_consent_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_document_atomic(text, text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.link_case_submission_atomic(text, text, text, text, jsonb) from public, anon, authenticated;

comment on table public.cases is 'RLS deny-by-default until canonical principal/case membership policy exists.';
comment on table public.consents is 'Purpose-bound consent; direct public API access remains denied by default.';
comment on table public.case_events is 'Append-only audit data; direct public API access remains denied by default.';
