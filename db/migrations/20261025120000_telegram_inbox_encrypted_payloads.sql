-- Encrypt transient Telegram payloads at rest and place a bounded deadline on them.
-- Existing payload-bearing rows are encrypted by PostgresTelegramInbox.secure_legacy_payloads()
-- during webhook startup, before the webhook is registered and accepts new work.
ALTER TABLE public.telegram_update_inbox
    ADD COLUMN IF NOT EXISTS encrypted_payload bytea;

ALTER TABLE public.telegram_update_inbox
    ADD COLUMN IF NOT EXISTS payload_expires_at timestamptz
    DEFAULT (now() + interval '24 hours');

-- Do not reset the retention clock of rows that were accepted long ago.
UPDATE public.telegram_update_inbox
SET payload_expires_at = LEAST(
    COALESCE(payload_expires_at, now() + interval '24 hours'),
    received_at + interval '24 hours'
)
WHERE status IN ('pending', 'processing')
  AND (payload IS NOT NULL OR encrypted_payload IS NOT NULL);

-- Expired legacy content is deleted during migration, before startup can re-encrypt it.
UPDATE public.telegram_update_inbox
SET status = 'dead_letter',
    payload = NULL,
    encrypted_payload = NULL,
    payload_expires_at = NULL,
    locked_at = NULL,
    processed_at = now(),
    last_error_code = 'payload_expired_during_migration'
WHERE status IN ('pending', 'processing')
  AND (payload IS NOT NULL OR encrypted_payload IS NOT NULL)
  AND payload_expires_at <= now();

-- A content-free receipt produced by the interim inline implementation cannot be replayed.
-- Preserve the update ID for audit/deduplication but move it to a terminal state instead of
-- allowing a pending row with no recoverable payload to block the same update forever.
UPDATE public.telegram_update_inbox
SET status = 'dead_letter',
    payload = NULL,
    encrypted_payload = NULL,
    payload_expires_at = NULL,
    locked_at = NULL,
    processed_at = now(),
    last_error_code = 'payload_missing_during_encryption_migration'
WHERE status IN ('pending', 'processing')
  AND payload IS NULL
  AND encrypted_payload IS NULL;

-- Terminal rows never retain any payload envelope or an expiry timestamp.
UPDATE public.telegram_update_inbox
SET payload_expires_at = NULL,
    encrypted_payload = NULL,
    payload = NULL
WHERE status IN ('processed', 'dead_letter');

ALTER TABLE public.telegram_update_inbox
    DROP CONSTRAINT IF EXISTS telegram_update_inbox_check;
ALTER TABLE public.telegram_update_inbox
    DROP CONSTRAINT IF EXISTS telegram_update_inbox_payload_state_check;
ALTER TABLE public.telegram_update_inbox
    DROP CONSTRAINT IF EXISTS telegram_update_inbox_payload_envelope_check;

ALTER TABLE public.telegram_update_inbox
    ADD CONSTRAINT telegram_update_inbox_payload_envelope_check
    CHECK (
        (
            status IN ('pending', 'processing')
            AND payload_expires_at IS NOT NULL
            AND (
                (payload IS NOT NULL AND encrypted_payload IS NULL)
                OR (payload IS NULL AND encrypted_payload IS NOT NULL)
            )
        )
        OR
        (
            status IN ('processed', 'dead_letter')
            AND payload IS NULL
            AND encrypted_payload IS NULL
            AND payload_expires_at IS NULL
        )
    );

CREATE INDEX IF NOT EXISTS telegram_update_inbox_encrypted_ready_idx
    ON public.telegram_update_inbox (available_at, received_at)
    WHERE status = 'pending'
      AND (payload IS NOT NULL OR encrypted_payload IS NOT NULL);

CREATE INDEX IF NOT EXISTS telegram_update_inbox_payload_expiry_idx
    ON public.telegram_update_inbox (payload_expires_at)
    WHERE status IN ('pending', 'processing');

COMMENT ON COLUMN public.telegram_update_inbox.payload IS
    'Legacy compatibility only. New webhook payloads are encrypted into encrypted_payload; startup encrypts old rows before registering the webhook.';

COMMENT ON COLUMN public.telegram_update_inbox.encrypted_payload IS
    'Fernet-encrypted JSON update using JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS; cleared on success, terminal dead-letter, or expiry.';

COMMENT ON COLUMN public.telegram_update_inbox.payload_expires_at IS
    'Maximum 24-hour processing window for pending/in-flight payloads. The running worker clears expired envelopes; data-at-rest remains ciphertext until cleanup runs.';
