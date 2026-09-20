-- Canonical external identity mapping.
-- A provider subject is never itself the Janavani principal.
CREATE TABLE IF NOT EXISTS public.external_identity_links (
    provider text NOT NULL,
    subject text NOT NULL,
    principal_id text NOT NULL,
    authentication_method text NOT NULL,
    verified boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (provider, subject)
);

CREATE INDEX IF NOT EXISTS external_identity_links_principal_idx
    ON public.external_identity_links(principal_id);

COMMENT ON TABLE public.external_identity_links IS
    'Verified mapping from a surface/provider identity to a canonical Janavani principal.';

COMMENT ON COLUMN public.external_identity_links.subject IS
    'Provider-scoped subject; never treated as the canonical citizen identity.';

COMMENT ON COLUMN public.external_identity_links.principal_id IS
    'Canonical Janavani principal identifier.';
