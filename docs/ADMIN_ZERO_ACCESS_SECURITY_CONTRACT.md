# JanaVani Admin Zero-Access Security Contract

**Status:** Architectural requirement
**Scope:** App, DApp, web, messaging adapters, AI services, storage, observability, support and administration

## 1. Non-negotiable rule

JanaVani backend administrators/operators MUST NOT be able to read, decrypt, inspect, export, or reconstruct sensitive user data.

Administrative access is operational access, not citizen-data access.

## 2. Data ownership boundary

The default ownership model is:

`User device -> user-controlled keys -> encrypted user data`

not:

`User -> JanaVani backend -> administrator`

Personal and sensitive user data should remain on the user's device unless a capability explicitly requires transmission. When transmission is required, only the minimum necessary data is sent, encrypted in transit and, where practical, end-to-end encrypted so the JanaVani service operator cannot decrypt it.

## 3. Admin-visible data classes

Administrators may access only operational metadata that is necessary to run the service, such as:

- service health;
- aggregate capacity and error metrics;
- anonymized or pseudonymized telemetry where enabled;
- abuse/security signals that do not expose protected content;
- public records and public civic datasets;
- system audit events that exclude sensitive payloads.

Administrators MUST NOT receive routine access to:

- complaint/private-draft contents;
- private messages;
- identity documents;
- private addresses or contact details;
- private location history;
- wallet seeds/private keys;
- private credentials/tokens;
- private AI prompts or outputs;
- private OCR/VLM/CV inputs or extracted content;
- private files, photographs, recordings or attachments;
- private RAG indexes or embeddings that can reveal user content;
- sensitive civic participation history;
- private financial contribution records beyond the minimum information strictly required for an independently governed transaction/reconciliation function.

## 4. Cryptographic enforcement

This requirement MUST NOT depend only on policy or administrator promises.

Where sensitive data is stored remotely, architecture SHOULD use client-held encryption keys, envelope encryption, capability-scoped keys, or end-to-end encryption such that the service operator does not possess the decryption material.

Server-side logs MUST NOT contain plaintext sensitive payloads.

Secrets MUST NOT be embedded in browser/mobile/DApp clients.

## 5. Support and recovery

Support staff MUST NOT be given a privileged "view user data" function.

Recovery designs MUST preserve the same boundary. If a recovery mechanism can decrypt all user data for an administrator, it violates this contract.

Users may explicitly export or share their own information with a destination of their choice.

## 6. Independent capability rule

No capability may weaken this boundary merely because it is implemented through a centralized backend.

AI, Agentic AI, SLM, RAG, VLM, LAM, MoE, MLM, SAM, LLM, OCR, computer vision, Web3, blockchain/ZKP, Nostr, Nym, Reticulum, Freenet, Telegram, WhatsApp, Messenger, web and native applications are separate capability domains. Failure or compromise of one capability MUST NOT grant access to unrelated user data.

## 7. Privacy-preserving observability

Operational telemetry SHOULD be:

- aggregate-first;
- data-minimized;
- redacted;
- retention-limited;
- independently auditable;
- disabled by default when not necessary for the capability.

Debug modes MUST never silently bypass the zero-access boundary.

## 8. Engineering acceptance tests

Future implementation must include tests proving that:

1. administrators cannot retrieve plaintext sensitive records;
2. backend logs do not contain protected payloads;
3. server databases contain only intentionally server-owned/public/minimized data;
4. client private keys are never transmitted as administrative credentials;
5. a compromised capability cannot access another capability's protected store;
6. deletion/export operates at the user-controlled data layer;
7. disabled optional capabilities do not receive user data;
8. AI providers receive only explicitly authorized/minimized inputs;
9. support tooling cannot escalate into content access;
10. production configuration cannot enable a hidden plaintext inspection path.

## 9. Constitutional and civic posture

JanaVani is designed as a citizen-governance infrastructure ecosystem. Privacy is therefore an architectural protection of citizen autonomy, not merely a commercial privacy feature.

This contract is subordinate to applicable Indian law and must be implemented consistently with the project's constitutional and civic principles.

## 10. Design principle

> **The administrator may operate the system without owning the citizen's data.**

That principle should remain true even if JanaVani scales to millions of users, adds new transports/protocols, or introduces future Web3/Web4/Web5/Web6-compatible capabilities.
