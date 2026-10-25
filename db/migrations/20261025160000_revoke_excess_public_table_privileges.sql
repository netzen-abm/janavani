-- Defense-in-depth hardening for exposed public tables.
-- This deliberately does NOT enable RLS: identity/policy and live-schema
-- reconciliation remain separate production gates.
-- Direct Case-data access stays on the trusted API/repository boundary.
-- Keep anonymous SELECT on the public offices directory intact.
REVOKE TRUNCATE, REFERENCES, TRIGGER, MAINTAIN
ON TABLE
    public.civic_cases,
    public.civic_case_events,
    public.civic_case_evidence_refs,
    public.civic_case_document_refs,
    public.civic_case_consents,
    public.civic_case_submissions,
    public.janavani_delegation_grants,
    public.janavani_service_identity_policies,
    public.offices
FROM anon, authenticated, service_role;
