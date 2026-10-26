# Superseded Telegram Content-Free Receipt Proposal

**Disposition date:** 25 October 2026  
**Status:** Superseded before production deployment; do not apply as an independent migration.

An interim design recorded Telegram update IDs and status/lease metadata without preserving the parsed update body. The webhook processed updates inline and depended on Telegram retry delivery for recovery. This reduced durable narrative persistence, but a provider's retry window is not an application-owned durable queue: an update could become unrecoverable if retries were exhausted after a long outage.

The proposal was replaced by the canonical migration `db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql`. The replacement keeps the existing PostgreSQL inbox/worker boundary, encrypts payloads using an out-of-band Fernet key ring, limits the processing window to 24 hours, and clears payloads on success or terminal failure. The old proposal was never accepted as the production retention/recovery contract.

The historical interim source and tests remain available in Git commit history for audit provenance. Do not copy this receipt-only design back into production without a documented decision acknowledging its weaker recovery guarantee.
