# Janavani Responsibility Resolution Contract

**Date:** 2026-09-10
**Status:** Implemented as a provider-neutral contract; production data resolution is not activated.

## Purpose

Janavani should reduce the distance between a citizen observation and the institution, asset, project, contract, obligation, or remedy that may be relevant to action.

The canonical primitive is:

```text
Observation → Responsibility Resolution → Evidence → Case → Action
```

This is a reusable civic capability, not a pothole-specific application.

## Resolution boundary

A resolution may contain candidate links to:

- asset or service
- jurisdiction
- authority / department / office
- project or programme
- contract / tender
- contractor / vendor
- responsible role
- obligation / warranty
- remedy or action channel

The contract intentionally does not declare guilt, corruption, misconduct, contractual breach, criminality, or final legal responsibility.

## Confidence model

Resolution results distinguish:

1. `observed` — directly supplied/observed fact
2. `high_confidence` — strong location/jurisdiction or matching signal
3. `matched_record` — directly matched source record
4. `probable` — useful candidate requiring verification
5. `verification_required` — unresolved relationship requiring human/source verification

Inference must never silently become an authoritative fact.

## Source rule

Every returned responsibility link must retain traceable `source_refs`. A resolution without traceable source evidence fails closed at the capability boundary.

## AI boundary

AI may assist with extraction, matching, classification, geolocation, record discovery, duplicate detection, and candidate ranking. AI output is not itself the authoritative source for responsibility.

## Citizen control

Responsibility resolution informs a Case. It does not submit an action automatically. The existing Case/document/submission boundaries remain authoritative for lifecycle, review, approval, consent, delivery, acknowledgement, and citizen outcome verification.

## Next integration

The next implementation should connect this contract to verified public records through provider-neutral adapters, beginning with jurisdiction/authority resolution and then project/contract/warranty relationships. No provider should become the canonical domain authority.
