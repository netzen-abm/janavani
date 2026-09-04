# CivicCase Lifecycle Semantics

## Purpose

This document records the semantic boundary of the canonical CivicCase lifecycle before additional domain mutations are introduced.

The lifecycle graph is shared by all Janavani access surfaces. A status being present in the graph does not, by itself, authorize a new command, event, or adapter behavior. A mutation is added only when its business meaning and evidence are established.

## Canonical lifecycle

The current canonical transition contract is:

```text
DRAFT -> REVIEW
REVIEW -> REVIEW | READY
READY -> READY | SUBMITTING
SUBMITTING -> SUBMITTING | QUEUED | SUBMITTED
QUEUED -> QUEUED | SUBMITTED
SUBMITTED -> ACKNOWLEDGED
ACKNOWLEDGED -> FOLLOW_UP | IN_PROGRESS | RESPONDED | ESCALATED
FOLLOW_UP -> FOLLOW_UP | RESPONDED | ESCALATED
IN_PROGRESS -> FOLLOW_UP | RESPONDED | ESCALATED
RESPONDED -> FOLLOW_UP | RESOLVED | ESCALATED
RESOLVED -> CLOSED
ESCALATED -> RESPONDED | CLOSED
CLOSED -> ARCHIVED
ARCHIVED -> none
```

## Status meanings

### ACKNOWLEDGED

`ACKNOWLEDGED` is the delivery boundary. It means Janavani has evidence that the submission was acknowledged by the receiving authority/system. It does not mean the authority has started processing the matter.

This distinction is already part of the domain contract and must remain explicit: submission and acknowledgement are different facts.

### IN_PROGRESS

`IN_PROGRESS` represents an operational state in which the receiving authority is understood to have begun processing the case.

The current domain model deliberately does **not** expose a direct `in_progress()` mutation and does not define a dedicated `IN_PROGRESS` event type. Therefore:

- do not add a citizen-facing `in_progress()` command yet;
- do not infer `IN_PROGRESS` merely from acknowledgement;
- do not invent an event type solely to make the transition executable;
- treat the lifecycle edge as a reserved canonical state until an authoritative source/event contract is defined.

When this is implemented, the source of the state transition must be explicit (for example, an authority update, verified status feed, or another defined operational signal) and must preserve provenance.

### ARCHIVED

`ARCHIVED` represents post-closure retention/administrative lifecycle, not a new citizen outcome.

The current domain model does not expose an `archive()` mutation. Therefore:

- `CLOSED` remains the citizen-facing terminal outcome state;
- do not add archive behavior to citizen workflows merely because the graph contains `CLOSED -> ARCHIVED`;
- do not treat archival as resolution, delivery, or submission;
- implement archival only after retention, access-control, provenance, and storage semantics are defined.

## Event/status boundary

Not every `CaseEventType` is a status transition. Evidence, document, edit, and correction events are orthogonal domain facts and must remain outside the lifecycle transition graph.

Likewise, a lifecycle status may exist before the domain exposes a corresponding mutation. The canonical graph is therefore a constraint on legal state movement, not a command inventory.

## Self-transitions

The current graph contains selected self-transitions (`REVIEW`, `READY`, `SUBMITTING`, and `QUEUED`, plus follow-up/in-progress operational states). These are retained for compatibility with the existing contract. They must not automatically create new business semantics or event types; idempotency should be handled deliberately when command contracts are added.

## Implementation rule

Before adding a new lifecycle mutation to `janavani-core`, establish all four items:

1. **Business meaning** — what real-world fact does the status represent?
2. **Authority/source** — who or what is allowed to assert that fact?
3. **Event contract** — what canonical event records the fact, including provenance?
4. **Cross-surface behavior** — how do Web, Telegram, mobile, and other adapters consume the same operation without reimplementing it?

Until those are defined, preserving the state in the canonical lifecycle graph without exposing an invented mutation is intentional and safer than premature domain expansion.
