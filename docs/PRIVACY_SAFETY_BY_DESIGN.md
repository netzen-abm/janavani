# Janavani Privacy & Safety by Design and by Default

**Status:** GOVERNING ARCHITECTURAL REQUIREMENT  
**Date:** 25 August 2026

## Principle

Privacy and safety are not optional ecosystem features. They are baseline properties of Janavani and must be designed into capabilities, infrastructure, adapters, clients and deployment from the beginning and enabled by default.

User choice controls whether a capability is used. It does **not** remove the capability from the ecosystem and does not turn off baseline privacy or safety protections.

## Distinction: capability choice versus baseline protection

```text
Capability exists
      |
      +--> user may use it
      +--> user may decline it
      |
      +--> privacy protections remain active
      +--> safety protections remain active
      +--> audit/provenance rules remain active
```

Examples:

- A user declining AI does not disable privacy protections.
- A user declining Web3 does not disable identity or authorization safeguards.
- A user declining a messaging channel does not change evidence/provenance protections.
- A user enabling Agentic AI does not waive scoped permissions or confirmation requirements.

## Privacy defaults

Implementations should default to:

1. data minimization;
2. purpose limitation;
3. least-privilege access;
4. explicit consent where required;
5. no unnecessary cross-client data sharing;
6. no provider-specific data export unless authorized and required;
7. local processing where practical for sensitive workflows;
8. encryption in transit and at rest where applicable;
9. auditable access and consequential actions;
10. explicit retention/deletion policy rather than indefinite retention;
11. provenance for important claims and derived analysis;
12. user-visible explanation of material data use.

A feature must not require the user to discover and manually enable basic privacy protection.

## Safety defaults

Implementations should default to:

1. least privilege;
2. deny-by-default access for protected operations;
3. explicit authorization for consequential actions;
4. human confirmation for high-impact external actions;
5. scoped and expiring Agentic AI tool permissions;
6. input validation and output validation;
7. rate limiting and abuse controls where appropriate;
8. safe failure rather than false success;
9. clear queued/sent/acknowledged/failed/unknown delivery states;
10. auditability for consequential actions;
11. isolation between independent clients and capabilities;
12. graceful degradation when optional execution paths fail.

## AI and Agentic AI

AI output is analysis unless supported by identified evidence. It must not silently become the sole source of truth.

Agentic AI must operate through scoped tool permissions. High-impact actions require explicit authorization and appropriate user confirmation. Agent actions must be auditable.

AI provider selection must remain replaceable. No single model/provider may become a universal dependency.

## Web3 / decentralized infrastructure

Nostr, Nym, Reticulum, Freenet, blockchain, ZKP and future decentralized technologies are integrated through capability and adapter contracts.

Their use must not silently expose additional user data, create irreversible actions, or become a mandatory dependency for unrelated workflows.

Decentralized verification, identity or anchoring must have explicit policy, consent and recovery semantics where applicable.

## Independent surface isolation

Web, Android, iOS, DApp, Telegram, Telegram Mini App, WhatsApp, Messenger and future surfaces must not require one another for baseline operation.

A failure or compromise in one surface must not automatically grant access to another surface or shared capability.

Shared infrastructure must enforce authorization at the capability boundary rather than relying on a client to behave correctly.

## Data and evidence separation

The system must distinguish:

```text
raw user input
     ↓
evidence
     ↓
analysis
     ↓
action
     ↓
outcome / verification
```

AI-generated analysis must not be represented as verified evidence without an explicit verification step.

Citizen reports, allegations, official responses and verified findings must remain distinguishable.

## Security and privacy review gate

A new capability or adapter is not considered production-ready merely because its code works.

The progression is:

`DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → FAILURE-ISOLATED → PRODUCTION-READY`

Security/privacy verification must include negative tests where practical:

- missing/invalid authorization;
- unauthorized cross-user access;
- provider outage;
- transport outage;
- malformed input;
- prompt/tool abuse for AI/Agentic capabilities;
- duplicate/replay actions;
- partial delivery;
- stale credentials;
- excessive data request;
- disabled user capability;
- compromised/failed adapter.

## Documentation requirement

Every new implementation that processes personal data, invokes external providers, performs consequential actions, uses AI/Agentic AI, or introduces a new transport must document its privacy and safety behavior in the same change set.

The architecture principles already require explicit consent, permissions, failure isolation, provenance, scoped agent permissions and privacy/security verification. This document makes those requirements a first-class implementation gate rather than a later review step.
