-- New webhook deliveries retain only update IDs and workflow status.
-- Payload-bearing rows are supported only as a temporary compatibility path for
-- work accepted by the earlier durable-payload implementation.
ALTER TABLE public.telegram_update_inbox
    DROP CONSTRAINT IF EXISTS telegram_update_inbox_check;
ALTER TABLE public.telegram_update_inbox
    DROP CONSTRAINT IF EXISTS telegram_update_inbox_payload_state_check;

ALTER TABLE public.telegram_update_inbox
    ADD CONSTRAINT telegram_update_inbox_payload_state_check
    CHECK (payload IS NULL OR status IN ('pending', 'processing'));

COMMENT ON COLUMN public.telegram_update_inbox.payload IS
    'NULL for content-free webhook receipts; non-NULL only for compatibility backlog accepted by the earlier durable-payload implementation. '
    'New webhook delivery must never persist raw Telegram JSON.';
