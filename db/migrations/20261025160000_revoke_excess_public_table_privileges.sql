-- Defense-in-depth hardening for exposed public tables.
-- This deliberately does NOT enable RLS: the identity/policy and live-schema
-- reconciliation gate remains open. It removes privileges clients do not need.
-- Keep anonymous SELECT on the public offices directory intact.
REVOKE TRUNCATE, REFERENCES, TRIGGER
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
