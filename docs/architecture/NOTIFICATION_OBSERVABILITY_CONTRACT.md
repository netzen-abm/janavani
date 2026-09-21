# Janavani Notification and Observability Contract

**Status:** ACTIVE ARCHITECTURE CONTRACT
**Date:** 2026-09-21

## Purpose

Provide one shared notification/observability boundary for the ecosystem.
Operational alerting is infrastructure, not a domain capability.

## Ownership

- Detection: observability/metrics layer.
- Decision: policy/threshold configuration.
- Notification: shared notification capability.
- Provider: email, webhook, push or other transport adapters.
- Surface: presentation only.

## Rules

1. No domain service constructs SMTP, Telegram, WhatsApp or another provider directly.
2. Provider credentials remain outside capability code.
3. Notification delivery must report truthful attempt/result state.
4. Failure of one provider must not imply failure of the capability.
5. Notifications must not mutate Case, Authority, Evidence or Submission state.
6. Security-sensitive notifications must avoid unnecessary personal data.
7. Alert thresholds and recipients are configuration/policy, not hard-coded service logic.
8. The capability must be independently testable without a live provider.

## Canonical flow

`Detection → Policy Decision → Notification Request → Provider Adapter → Truthful Result → Audit Evidence`

## Migration

The former `src/services/watchdog.py` contained duplicate implementations and direct SMTP construction, with no confirmed active caller. Its source was archived before removal. Future alerting must use this contract rather than recreating a watchdog service.
