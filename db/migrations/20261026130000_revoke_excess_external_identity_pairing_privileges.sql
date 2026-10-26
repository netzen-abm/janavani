-- Pairing challenges contain short-lived identity-linking state.
-- Keep database-structural privileges away from API-facing and service roles.
-- The dedicated identity-link runtime role retains its separately granted DML.
REVOKE TRUNCATE, REFERENCES, TRIGGER
    ON TABLE public.external_identity_pairings
    FROM PUBLIC, anon, authenticated, service_role;
