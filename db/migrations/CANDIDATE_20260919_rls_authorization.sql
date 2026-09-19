-- Janavani — candidate PostgreSQL RLS policy set
-- STATUS: CANDIDATE ONLY / NOT ACTIVATED
-- This migration MUST NOT be applied until the application establishes a
-- trusted transaction-local janavani.principal_id for the database session
-- and the database role is confirmed not to bypass RLS.
--
-- The application identity model uses opaque text principal IDs, not auth.uid().
-- Therefore this candidate deliberately does not depend on Supabase Auth.

CREATE SCHEMA IF NOT EXISTS janavani_private;

CREATE OR REPLACE FUNCTION janavani_private.current_principal_id()
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('janavani.principal_id', true), '')
$$;

-- Case ownership / active delegation.
ALTER TABLE public.civic_cases ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS civic_cases_owner_select ON public.civic_cases;
CREATE POLICY civic_cases_owner_select
ON public.civic_cases
FOR SELECT
USING (
    created_by = janavani_private.current_principal_id()
    OR EXISTS (
        SELECT 1
        FROM public.janavani_delegation_grants d
        WHERE d.grantor_id = civic_cases.created_by
          AND d.delegate_id = janavani_private.current_principal_id()
          AND d.revoked = false
          AND (d.expires_at IS NULL OR d.expires_at > now())
          AND (
              d.resource_ids = '[]'::jsonb
              OR d.resource_ids @> jsonb_build_array(civic_cases.case_id)
          )
    )
);

DROP POLICY IF EXISTS civic_cases_owner_insert ON public.civic_cases;
CREATE POLICY civic_cases_owner_insert
ON public.civic_cases
FOR INSERT
WITH CHECK (
    created_by = janavani_private.current_principal_id()
    OR EXISTS (
        SELECT 1
        FROM public.janavani_delegation_grants d
        WHERE d.grantor_id = civic_cases.created_by
          AND d.delegate_id = janavani_private.current_principal_id()
          AND d.revoked = false
          AND (d.expires_at IS NULL OR d.expires_at > now())
          AND d.actions @> '["case:update"]'::jsonb
          AND (
              d.resource_ids = '[]'::jsonb
              OR d.resource_ids @> jsonb_build_array(civic_cases.case_id)
          )
    )
);

DROP POLICY IF EXISTS civic_cases_owner_update ON public.civic_cases;
CREATE POLICY civic_cases_owner_update
ON public.civic_cases
FOR UPDATE
USING (
    created_by = janavani_private.current_principal_id()
    OR EXISTS (
        SELECT 1
        FROM public.janavani_delegation_grants d
        WHERE d.grantor_id = civic_cases.created_by
          AND d.delegate_id = janavani_private.current_principal_id()
          AND d.revoked = false
          AND (d.expires_at IS NULL OR d.expires_at > now())
          AND d.actions @> '["case:update"]'::jsonb
          AND (
              d.resource_ids = '[]'::jsonb
              OR d.resource_ids @> jsonb_build_array(civic_cases.case_id)
          )
    )
)
WITH CHECK (
    created_by = janavani_private.current_principal_id()
);

-- Child records inherit authorization from their Case.
ALTER TABLE public.civic_case_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_evidence_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_document_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_submissions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS civic_case_events_case_access ON public.civic_case_events;
CREATE POLICY civic_case_events_case_access
ON public.civic_case_events
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.civic_cases c
        WHERE c.case_id = civic_case_events.case_id
    )
);

DROP POLICY IF EXISTS civic_case_evidence_case_access ON public.civic_case_evidence_refs;
CREATE POLICY civic_case_evidence_case_access
ON public.civic_case_evidence_refs
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.civic_cases c
        WHERE c.case_id = civic_case_evidence_refs.case_id
    )
);

DROP POLICY IF EXISTS civic_case_document_case_access ON public.civic_case_document_refs;
CREATE POLICY civic_case_document_case_access
ON public.civic_case_document_refs
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.civic_cases c
        WHERE c.case_id = civic_case_document_refs.case_id
    )
);

DROP POLICY IF EXISTS civic_case_submission_case_access ON public.civic_case_submissions;
CREATE POLICY civic_case_submission_case_access
ON public.civic_case_submissions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.civic_cases c
        WHERE c.case_id = civic_case_submissions.case_id
    )
);

-- Consent follows subject identity, not case visibility.
ALTER TABLE public.civic_case_consents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS civic_case_consents_subject_access ON public.civic_case_consents;
CREATE POLICY civic_case_consents_subject_access
ON public.civic_case_consents
FOR SELECT
USING (
    subject_id = janavani_private.current_principal_id()
);

-- Delegations: grantor may manage; delegate may inspect active grants.
ALTER TABLE public.janavani_delegation_grants ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS janavani_delegation_grant_access ON public.janavani_delegation_grants;
CREATE POLICY janavani_delegation_grant_access
ON public.janavani_delegation_grants
FOR SELECT
USING (
    grantor_id = janavani_private.current_principal_id()
    OR delegate_id = janavani_private.current_principal_id()
);

DROP POLICY IF EXISTS janavani_delegation_grant_insert ON public.janavani_delegation_grants;
CREATE POLICY janavani_delegation_grant_insert
ON public.janavani_delegation_grants
FOR INSERT
WITH CHECK (
    grantor_id = janavani_private.current_principal_id()
);

DROP POLICY IF EXISTS janavani_delegation_grant_update ON public.janavani_delegation_grants;
CREATE POLICY janavani_delegation_grant_update
ON public.janavani_delegation_grants
FOR UPDATE
USING (grantor_id = janavani_private.current_principal_id())
WITH CHECK (grantor_id = janavani_private.current_principal_id());

-- Service identity policy state is backend-controlled. Ordinary database
-- sessions receive no policy that permits reading or changing these rows.
ALTER TABLE public.janavani_service_identity_policies ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.janavani_service_identity_policies FROM anon, authenticated;

-- No DELETE policies are intentional: lifecycle/history removal must remain
-- behind dedicated capability/service boundaries.
