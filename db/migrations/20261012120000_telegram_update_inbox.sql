-- Durable Telegram webhook inbox.
-- Payloads are retained only while work is pending/in-flight and are cleared on
-- terminal completion to reduce retention of citizen message content.
CREATE TABLE IF NOT EXISTS public.telegram_update_inbox (
    update_id bigint PRIMARY KEY,
    payload jsonb,
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'processed', 'dead_letter')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    received_at timestamptz NOT NULL DEFAULT now(),
    available_at timestamptz NOT NULL DEFAULT now(),
    locked_at timestamptz,
    processed_at timestamptz,
    last_error_code text,
    CHECK (
        (status IN ('pending', 'processing') AND payload IS NOT NULL)
        OR (status IN ('processed', 'dead_letter') AND payload IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS telegram_update_inbox_ready_idx
    ON public.telegram_update_inbox (available_at, received_at)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS telegram_update_inbox_stale_idx
    ON public.telegram_update_inbox (locked_at)
    WHERE status = 'processing';

REVOKE ALL ON TABLE public.telegram_update_inbox FROM PUBLIC;

COMMENT ON TABLE public.telegram_update_inbox IS
    'Durable, idempotent Telegram update acceptance; terminal rows retain update IDs but not message payloads.';
