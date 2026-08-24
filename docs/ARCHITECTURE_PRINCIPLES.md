# JanaVani Architecture Principles

This document converts the ecosystem charter into engineering rules that can be tested during implementation and review.

## A. Independence

1. Every major capability is independently deployable or replaceable where technically practical.
2. Optional capabilities must not become hidden dependencies.
3. A failure in one capability must not cascade into unrelated capabilities.
4. Interfaces must consume capability contracts rather than importing implementation details from other capabilities.
5. External providers are adapters, not the domain model.

## B. User Choice

1. Capabilities are available to the ecosystem even when a particular user does not enable them.
2. User activation, consent, permissions and data sharing are explicit.
3. Disabling an optional capability must preserve unrelated functionality.
4. Capability settings must explain data use and degraded behavior.

## C. Local-first and Resilience

1. Local state should survive temporary network/provider failure.
2. Offline or degraded paths should exist for critical workflows where practical.
3. Network adapters must expose health, retry, timeout and recovery behavior.
4. Delivery status must distinguish queued, sent, acknowledged, failed and unknown states.

## D. Evidence and Provenance

1. Evidence, analysis and action are separate layers.
2. AI output is analysis unless supported by identified evidence.
3. Important claims should carry source/provenance metadata.
4. User corrections to authoritative information require verification and audit history.
5. Citizen reports, allegations, official responses and verified findings must remain distinguishable.

## E. AI Independence

OCR, CV, SAM, VLM, SLM, LLM, MLM, MoE, LAM, RAG, Agentic AI, translation and other intelligence capabilities are separate contracts/providers. No single model or provider is the universal dependency for JanaVani.

AI must not silently become the sole source of truth. Critical workflows should have deterministic, human-review or degraded paths where appropriate.

## F. Agentic Safety

Agentic systems must use scoped tool permissions. High-impact external actions require explicit authorization and appropriate user confirmation. Actions must be auditable.

## G. Technology Neutrality

JanaVani must not encode Web2/Web3/Web4/Web5/Web6 as a replacement hierarchy. New technologies are added through adapters and capability contracts.

Freenet, Nostr, Nym, Reticulum, blockchain and ZKP are first-class ecosystem capabilities with explicit user participation controls; none should be an accidental universal dependency.

## H. Client Independence

Android, iOS, WebApp, DApp, Telegram, Telegram Mini App, WhatsApp and Messenger are access surfaces. Business logic belongs in shared capabilities/contracts, not in a single client.

## I. Financial Integrity

Contribution functionality must remain isolated and auditable. Financial records should support source, authorization, transaction, allocation, expenditure evidence, audit and reporting. Decentralized verification may be optional.

## J. Verification

Every capability progresses through:

`VISION -> DESIGNED -> IMPLEMENTED -> FUNCTIONAL -> TESTED -> SECURITY-VERIFIED -> PRIVACY-VERIFIED -> FAILURE-ISOLATED -> PRODUCTION-READY`

Architecture tests should deliberately disable or break optional dependencies and verify that unrelated functionality remains available.

## K. Evolution

A new feature should normally require adding or implementing a capability contract, adapter, manifest, permissions, tests and documentation—not rewriting unrelated clients or the core.

If an implementation violates these principles, record an Architecture Decision Record explaining why, the scope of the exception, and how the dependency will be contained or removed.
