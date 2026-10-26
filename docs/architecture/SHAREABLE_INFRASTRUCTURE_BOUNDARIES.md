# Janavani Shareable Infrastructure Responsibility Boundaries

## Purpose

Janavani is converging on a shared infrastructure model in which capabilities are implemented once and consumed by independent access surfaces. This document defines where code should be separated and where cohesion must be preserved.

## Canonical rule

Split code only when the split creates an independent architectural boundary of:

- change/release cadence;
- trust, identity, authorization, or consent;
- persistence/transaction ownership;
- provider or external-system dependency;
- deployment/runtime isolation; or
- independent reuse by another surface or application.

Do not split merely because a file or class is large. Preserve cohesion when splitting would weaken invariants, fragment a state machine, obscure transaction semantics, or duplicate orchestration.

## Layer boundaries

```text
Access Surface / Adapter
        |
Application / Use Case
        |
Shared Capability
        |
Domain + Workflow + Policy
        |
Provider-Neutral Contract
        |
Provider Adapter / Persistence / External System
```

### Access surfaces

WebApp, Telegram, WhatsApp, Messenger, mobile clients, DApp and future surfaces are adapters. They may own transport-specific concerns, presentation, session mechanics and provider-specific composition, but must not become alternate owners of canonical domain workflows.

### Application/use-case layer

Owns cross-surface orchestration and consequential workflow sequencing. If WebApp and Telegram require the same business action, the action belongs here rather than being duplicated in both adapters.

### Shared capability layer

Owns reusable capability contracts and invariants such as Case, Evidence, Authority, Document, Consent, Submission and Tracking.

A capability should have one canonical owner.

### Domain/workflow/policy

Domain rules, lifecycle semantics, authorization decisions, consent semantics and workflow state transitions remain cohesive when they jointly protect the same invariant.

### Provider-neutral contracts

Define stable contracts between application/domain code and persistence or external providers. They should not contain PostgreSQL, Telegram, HTTP-client or other provider implementation details.

### Provider adapters

PostgreSQL repositories, transport providers, external authority integrations and similar implementations belong behind provider boundaries. Provider failure must not redefine the domain contract.

## Persistence rule

Transaction ownership is an architectural boundary.

For example:

- Case-only mutations use the canonical Case transaction boundary.
- Submission + Case mutations use the atomic SubmissionCase transaction boundary.
- External delivery is not part of the database transaction.

Do not split these boundaries further unless a new independent invariant or provider boundary emerges.

## Trust rule

Identity, authorization, consent and capability execution are separate trust concerns.

A transport identity is not automatically a citizen identity. User-supplied actor identifiers must not become trusted authorization context. Consequential actions require explicit policy and consent gates.

## Surface-independence rule

A surface may fail without disabling another surface.

Therefore:

- Telegram is an adapter, not the Case system.
- WebApp is an adapter, not the Case system.
- Shared capabilities do not depend on a specific transport.
- Provider-specific failures are contained at their boundary.

## AI and agent rule

AI is a replaceable capability/provider layer, not the source of truth.

AI may assist with extraction, drafting, classification or other explicitly bounded purposes. It must not silently become the authority for facts, identity, authorization, consent or consequential decisions.

Agent execution must remain capability-scoped and policy-gated.

## Archive-first repository hygiene

Historical branches and superseded implementations must be archived before deletion. A branch may be deleted only after:

1. its unique work has been reviewed for extraction or convergence;
2. any retained work exists in a canonical branch or immutable archive reference;
3. open-PR dependencies are resolved;
4. deletion does not remove the only recoverable copy.

The target is exactly eight active development roles. Until the controlled transition in PR #213 finishes, the physical inventory may include one temporary retirement-only branch. The target is not achieved until a fresh GitHub query confirms exactly eight physical refs. The eventual product-ready target is one canonical `main` branch, after useful work has been preserved and release evidence passes. See `docs/90-audits/2026-10-25-engineering-proof-cycle-and-repository-structure-audit.md`.

## Current convergence decision

The current repository should not introduce another Case repository, Web framework, Telegram workflow, AI orchestration layer or parallel capability implementation merely to reduce file size.

The next engineering work should preferentially be:

1. selective extraction of genuinely unique work from sanctioned divergent branches;
2. verification of canonical WebApp/Telegram end-to-end behavior;
3. provider and persistence production gates;
4. shared capability reuse across future surfaces.

## Completion standard

A capability is not considered complete merely because its code exists. Promote it through:

VISION -> DESIGNED -> IMPLEMENTED -> FUNCTIONAL -> TESTED -> SECURITY-VERIFIED -> PRIVACY-VERIFIED -> FAILURE-ISOLATED -> PRODUCTION-READY

## Repository hygiene enforcement

The eight sanctioned branch roles are the only intended active development lanes; PR #213 defines the controlled transition ref used to retire itself. Legacy branches are archived by immutable tag before deletion, with exact-head verification and a fresh physical inventory afterward. Do not treat the transition ref as a ninth approved development role, and do not claim eight-ref compliance before the deletion has been verified.


## Public website and dynamic workspace boundary

The `netzen-abm/janavani-website` repository is the static brochure/showcase and editorial layer, published through GitHub Pages. Its `JANAVANI-MASTER-WEBSITE-CONTENT-MAP.md` and six page content masters govern the public site's messaging, including citizen agency, clear current/building/future status, privacy and substantiated capability claims. Do not duplicate dynamic Case workflows, identity state, authority lookup or backend behavior into this static repository.

The dynamic citizen workspace belongs in the platform repository. WebApp, API and Telegram must remain independently deployable adapters over the same canonical capabilities and persistence contracts. Do not describe a workspace route as publicly available until its intended production deployment, public reachability, OIDC trust boundary, API endpoint, durable providers and citizen-journey acceptance have been verified.

Shared website assets should be reused only where a genuine presentation contract exists. The public brochure site and authenticated citizen WebApp may share approved brand tokens and content principles; they must not share session state, citizen content, authorization logic or deployment assumptions.

## Deployment-provider neutrality

Render and Vercel are currently used only as temporary testing/validation environments. They are deployment adapters, not architectural dependencies. Do not introduce code paths, domain abstractions, persistence assumptions, identity flows, authorization rules, consent semantics, or capability contracts specifically to accommodate either provider.

The canonical platform must remain provider-neutral so that hosting can be changed without changing the shared ecosystem architecture. Deployment configuration belongs at the outer deployment boundary; application/domain/provider contracts remain independently testable.
