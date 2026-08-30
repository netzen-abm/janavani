# Civic Issue → Authority → Action Routing

## Purpose

A citizen may know the problem but not know the responsible authority. Janavani must solve this as a shared capability, independent of Web, Telegram, Mini App, mobile, or future access surfaces.

## Canonical flow

```text
Citizen language
      ↓
Issue extraction
      ↓
Issue classification
      ↓
Location / jurisdiction (only when needed)
      ↓
Authority candidates
      ↓
Authoritative-source verification
      ↓
Ranked pathway
      ↓
Citizen confirmation when ambiguity remains
      ↓
Action type
      ↓
Document / next step
```

## No guessing

The system must not invent an authority, postal address, official email, jurisdiction, or legal requirement. If confidence is insufficient or sources conflict, the user must see the uncertainty and be asked for the minimum missing information or offered a manual path.

## Examples

- Broken road → identify responsible local/public-works authority based on location and jurisdiction.
- Delayed Panchayat service → identify the service, responsible office, escalation path, and applicable local jurisdiction.
- Broken water pipeline → distinguish local body, water utility, public works, or other responsible provider using verified jurisdictional data.

The examples are patterns, not hard-coded routing rules.

## Authority data

Authority discovery should combine deterministic jurisdiction rules with verified public authority data. AI may assist classification or ranking but is not the source of truth for official contact details.

## Privacy

Issue routing should work with the minimum necessary context. Personal identity, sensitive case details, evidence, and private documents must not be sent to AI or external providers by default. Public locality/jurisdiction information should be separated from private case content.

## Multilingual input

The same semantic issue representation should be produced regardless of the citizen's input language. Language identification, normalization, and translation are infrastructure capabilities; routing rules remain language-neutral.

## Completion gate

Production readiness requires representative issue categories, jurisdiction tests, ambiguous-case handling, conflicting-source handling, freshness/provenance, multilingual tests, and deterministic fallback.
