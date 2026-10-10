-- Web↔Telegram pairing challenges. Store only the digest of the high-entropy
-- one-time code; identity mappings are written only after Web confirmation.
CREATE TABLE IF NOT EXISTS public.external_identity_pairings (
    pairing_id text PRIMARY KEY,
    token_digest char(64) NOT NULL UNIQUE,
    principal_id text NOT NULL,
    expires_at timestamptz NOT NULL,
    provider text,
    subject text,
    claimed_at timestamptz,
    confirmed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT external_identity_pairings_claim_shape CHECK (
        (provider IS NULL AND subject IS NULL AND claimed_at IS NULL)
        OR
        (provider = 'telegram' AND subject IS NOT NULL AND claimed_at IS NOT NULL)
    ),
    CONSTRAINT external_identity_pairings_confirm_requires_claim CHECK (
        confirmed_at IS NULL OR (provider = 'telegram' AND subject IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS external_identity_pairings_expiry_idx
    ON public.external_identity_pairings(expires_at);

COMMENT ON TABLE public.external_identity_pairings IS
    'Short-lived Web↔Telegram identity pairing state; challenges expire and are single-use.';
COMMENT ON COLUMN public.external_identity_pairings.token_digest IS
    'SHA-256 digest of a high-entropy one-time code; raw codes are never persisted.';
