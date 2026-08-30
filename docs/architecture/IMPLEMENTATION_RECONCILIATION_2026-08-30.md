# JanaVani Core Implementation Reconciliation — 2026-08-30

## Purpose

Reconcile the shared civic core before adding another capability. This document records repository-state findings, scope decisions, and the canonical implementation direction.

## Verified core components

- `src/core/capabilities/issue_understanding.py`
- `src/core/capabilities/authority_discovery_service.py`
- `src/core/capabilities/legal_applicability.py`
- `src/core/capabilities/civic_action_planner.py`
- `src/core/capabilities/case_decision_engine.py`
- `src/core/capabilities/case_action_graph.py`
- `src/core/capabilities/case_continuity.py`
- `src/core/capabilities/case_state.py`
- `src/core/capabilities/civic_case_orchestrator.py`
- `src/core/contracts/case.py`
- `src/core/contracts/case_action_graph.py`
- `src/core/contracts/case_state.py`
- `src/core/contracts/legal_applicability.py`
- `src/core/contracts/legal_knowledge.py`
- `src/core/contracts/legal_source.py`
- `src/core/contracts/rti_knowledge.py`

## Reconciliation decisions

### Canonical orchestrator

`civic_case_orchestrator.py` is the canonical end-to-end composition layer. The older duplicate `case_orchestrator.py` implementation was removed to prevent parallel workflow semantics.

### Court-reference capability

Court-reference research is deferred to the future Legal Companion product. The incomplete `case_law_reference.py` implementation was removed because its contract had already been removed and the capability was outside the current JanaVani citizen-participation scope.

### Case state

Persistent case state remains metadata/workflow oriented. Raw personal or sensitive evidence is not permitted in shared case state. Original evidence should remain under the user's control, with only an appropriate local reference/provenance handle when required.

### Document boundary

Current JanaVani document generation ends at user-selected PDF/DOCX delivery. Submission by email, post, messaging, or other external channels is outside this current document capability unless separately enabled as a future ecosystem capability.

### Procedure/trigger rule

Follow-up and escalation must be driven by verified procedural facts, explicit case events, or user choice. Legal deadlines must never be invented or hard-coded without authoritative provenance and effective-date context.

## Canonical flow

Citizen narrative → issue understanding → authority discovery → legal applicability → verified procedure → civic action decision → case action graph → persistent case state/continuity → document preparation → user review → PDF/DOCX delivery.

## Verification gate

This reconciliation is an architecture/integration checkpoint, not a declaration that the entire ecosystem is complete. Production completion requires implementation, tests, verification, documentation, and master-checklist approval.
