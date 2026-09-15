# Canonical Escalation Capability

## Purpose

Escalation is a canonical, user-controlled decision derived from the Case state and event history. It is not an autonomous delivery operation.

The shared escalation boundary exists so Web, Telegram, Android, iOS, WhatsApp, Messenger, DApp, and future surfaces do not implement independent escalation rules.

## Boundary

`EscalationCapability` may:

- inspect canonical `CivicCase` state and history;
- consider an explicit user-reported outcome;
- recommend whether follow-up or escalation is appropriate;
- identify a bounded next escalation action;
- explain the reason for the recommendation.

`EscalationCapability` must not:

- mutate the Case;
- persist escalation state;
- send or submit anything externally;
- choose an unverified destination;
- bypass authorization, consent, explicit approval, or consequential-operation controls;
- assert misconduct, liability, guilt, or legal conclusions merely from an overdue case.

## Separation of responsibilities

- **FollowUpCapability** decides the adaptive next user-controlled follow-up action.
- **EscalationCapability** decides whether escalation is appropriate and what bounded next action can be considered.
- **Authority / Responsibility capabilities** identify traceable institutional responsibility.
- **External Channel capability** resolves verified control-plane channels.
- **SubmissionCapability** owns submission authorization, consent, approval, idempotency, delivery, and reconciliation.
- **DeliveryTransport** owns transport execution.

No legacy escalation service may become a hidden alternative to these boundaries.

## Legacy implementation status

The historical implementations `src/services/escalation_rules.py`, `src/services/escalation_engine.py`, and the operational behavior of `src/services/escalation_runner.py` have been quarantined after repository-wide searches found no additional caller beyond the legacy chain itself.

Their original implementations are preserved under `archive/legacy/escalation/` for historical recovery. The active service paths no longer contain the historical category-target rules or JSONL mutation logic. The remaining compatibility entry points fail closed and direct callers to the canonical capability.

Deletion of the archived copies remains deferred under the repository's archive-first rule. Retirement evidence should be extended if future surfaces or deployment configuration reveal any historical dependency.

## Safety invariant

An escalation recommendation is not an escalation action. Any future external escalation must traverse the same canonical authorization, consent, explicit approval, verified-channel, submission, idempotency, delivery, and acknowledgement boundaries as other consequential civic actions.
