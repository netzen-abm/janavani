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

The repository still contains `src/services/escalation_rules.py`, `escalation_engine.py`, and `escalation_runner.py`. They are legacy code, not the canonical escalation boundary. They currently read and rewrite `database/ratings.jsonl`, derive category-based target lists, and change a complaint status while reporting `Escalated`.

They must therefore not be wired into access surfaces or treated as the source of truth for the canonical Case lifecycle. They should remain available for historical recovery until their behavior is either migrated to canonical capabilities or explicitly retired after evidence.

## Safety invariant

An escalation recommendation is not an escalation action. Any future external escalation must traverse the same canonical authorization, consent, explicit approval, verified-channel, submission, idempotency, delivery, and acknowledgement boundaries as other consequential civic actions.
