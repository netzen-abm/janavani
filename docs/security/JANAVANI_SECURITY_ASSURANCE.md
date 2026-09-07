# Janavani Security Assurance

**Status:** Canonical security architecture and release-gate specification  
**Scope:** Entire Janavani ecosystem  
**Principle:** Build security infrastructure once; capabilities and access surfaces consume it.

## 1. Purpose

This document adapts the five security checks reviewed for Janavani into a reusable security assurance system. The source checks cover secret-leak prevention, personal-data flow, production readiness, complex-logic security, and attacker-perspective review. Janavani extends those checks to its actual architecture: civic cases, evidence, documents, consent, AI and agents, independent access surfaces, local-first privacy, and a polyglot supply chain.

This document defines assurance requirements. It does not by itself prove that an implementation satisfies them.

## 2. Security Assurance System

```text
JANAVANI SECURITY ASSURANCE SYSTEM
├── 01 Secret Security
├── 02 Citizen Data-Flow Security
├── 03 Production Security
├── 04 Domain / Logic Security
├── 05 Adversarial Security
├── 06 AI & Agent Security
├── 07 Privacy Architecture
└── 08 Supply-Chain Security
```

## 3. Release Security Gate

```text
CODE
→ STATIC SECURITY
→ DEPENDENCY SECURITY
→ DATA-FLOW AUDIT
→ DOMAIN TESTS
→ ADVERSARIAL TESTS
→ RUNTIME TEST
→ PRIVACY REVIEW
→ HUMAN SECURITY REVIEW
→ RELEASE
```

A release is not considered security-assured merely because CI is green. Automated checks establish evidence for defined properties; human review remains required for consequential security decisions.

## 4. Secret Security

Required controls:

- Secrets must be supplied through protected environment/configuration mechanisms, never hard-coded.
- `.env` and equivalent local secret files must be ignored; `.env.example` may document required variable names without real values.
- Supabase service-role/secret credentials must never reach public clients. Client-side keys must be limited to the access model they are designed for and protected by appropriate row-level authorization.
- Stripe-style public/publishable credentials must be separated from secret credentials.
- Database connection strings and private provider credentials belong in protected runtime configuration.
- Sensitive values must not be placed in public/browser-exposed environment namespaces.
- Logs, errors, traces, API responses, CI output and generated artifacts must not disclose secrets.
- Security review must include current files and, where applicable, Git history, branches, pull requests, archives, container layers and CI/deployment configuration.
- If a real secret was committed, merely moving it to an environment variable is insufficient: revoke/rotate it and assess historical exposure before declaring the incident resolved.

## 5. Citizen Data-Flow Security

Janavani must model where citizen data is collected, transformed, stored, transmitted and deleted.

Required checks:

- Identify every collection point and every external integration.
- Classify data before a capability receives it.
- Minimize transmission to the minimum necessary for the selected purpose.
- Do not put sensitive personal data in logs, analytics, telemetry, URLs, crash reports or debugging output without an explicitly justified and protected design.
- Avoid unnecessary PII in browser local storage and client caches.
- Filter API responses to the minimum necessary fields.
- Define deletion and retention behavior for every persistent copy.
- Treat evidence originals, derivatives, OCR output and metadata as distinct data assets.
- Distinguish case location, evidence-capture location and current user location.
- Audit third-party providers for what data they receive and under which user-authorized purpose.

Janavani's intended boundary is local-first: the platform should not become a central personal-data collection system by default. "Local-first" does not mean that no data can ever leave the device; it means disclosure is explicit, minimized, purpose-bound and policy-controlled.

## 6. Production Security

Before production release, verify:

- All required runtime environment variables are present and correctly scoped.
- Debug/development paths are disabled where inappropriate.
- Errors are handled without exposing internals or secrets.
- Correlation/request identifiers are available without leaking sensitive data.
- Security headers and browser protections are configured appropriately.
- Rate limiting exists for abuse-sensitive endpoints and actions.
- CORS is explicit and least-privilege.
- Database/network connections use appropriate TLS/SSL protections.
- The production runtime is the canonical runtime rather than a legacy compatibility path.
- Render, Docker, local development, CI and any other deployment surface resolve to the intended application entrypoint.
- Independent access surfaces do not require another surface's process to remain alive.

## 7. Domain / Logic Security

Authorization must be enforced at the domain boundary, not only in UI controls.

Test at minimum for manipulation of:

- Case IDs
- Evidence IDs
- Document IDs
- Authority/office IDs
- Submission IDs
- User/owner identifiers
- Consent scopes
- Lifecycle transitions
- Review/approval state
- Provenance records
- Provider selection
- Agent permissions

Required adversarial properties include:

- No cross-user or cross-case access through identifier substitution (BOLA/IDOR).
- No privilege escalation through client-controlled role or state fields.
- Lifecycle transitions cannot bypass required review, consent or authorization.
- Consequential actions cannot be triggered merely by generating an AI output.
- Submission cannot be duplicated or replayed without an intentional, authorized workflow.
- Approval cannot be forged by modifying client-side state.
- Provenance cannot be silently rewritten.
- Provider substitution cannot silently change a user's authorized data boundary.

## 8. Adversarial Security

Threat review must consider at least:

- Anonymous Internet attacker
- Malicious citizen/user
- Compromised device
- Malicious authenticated user
- Cross-case attacker
- Malicious administrator/operator
- Compromised or malicious provider
- Malicious AI provider/model
- Prompt-injection and indirect-injection attacker
- Malicious agent/tool
- Compromised Telegram account or integration
- Supply-chain attacker/compromised dependency
- Insider
- Network attacker
- Malicious document/evidence payload

Test for authentication bypass, authorization bypass, identifier manipulation, privilege escalation, injection, file-upload abuse, rate-limit abuse, internal-service exposure, business-logic abuse, replay, cross-tenant leakage and unintended external actions.

## 9. AI & Agent Security

AI is a shared Janavani capability, but AI use is user-choice and must not weaken mandatory privacy/security controls.

Required controls:

- Prompt injection and indirect prompt injection testing.
- Data-exfiltration testing across model context, tools, RAG and integrations.
- Tool authorization independent of model instructions.
- Least-privilege tool scopes.
- Explicit user authorization for consequential actions such as submission, external messaging and public publishing.
- AI permission does not automatically grant action permission.
- Agent permissions must be scoped by capability, purpose, data class, provider, duration and action where applicable.
- Agents cannot expand their own permissions.
- Cross-user and cross-case context isolation.
- RAG/source poisoning and citation manipulation tests.
- Hallucination and unsupported-claim detection.
- Uncertainty/contradiction handling where the capability depends on factual reliability.
- Provider leakage and data-boundary verification.
- Agent loop, retry and autonomy-escalation controls.

**Security invariant:** AI may generate a claim; AI may not promote its own claim to verified fact.

## 10. Privacy Architecture

Privacy verification must cover:

- Data minimization
- Local-first storage
- Scoped consent
- Purpose limitation
- User-selected provider/capability where applicable
- Explicit transmission
- Encryption in transit and at rest where applicable
- Retention
- Deletion
- Metadata leakage
- Telemetry and analytics
- Error logging
- Cross-surface replication
- Browser storage
- Third-party integrations

Consent is not blanket permission. A valid consent model should identify the capability/purpose, relevant data, provider where material, duration where material, and consequential action being authorized.

## 11. Evidence Security

Evidence requires a dedicated security review because civic evidence may include photographs, video, GPS, timestamps, documents, OCR and derived artifacts.

Required invariants:

- Originals are never overwritten.
- Original evidence receives an integrity hash as close to capture/import as practical.
- OCR and edited previews are derived artifacts, not replacements for originals.
- Transformations are recorded where provenance matters.
- Capture time and submission time remain distinct.
- GPS privacy must be policy-controlled; exact coordinates must not be disclosed merely because they exist.
- Device attestation/signing claims must reflect actual implementation.
- Never claim hardware-backed, verified or signed unless the corresponding technical property has actually been established.
- Deletion and recovery behavior must be testable for each evidence store.
- Export/submission packages must preserve provenance and integrity metadata required by the selected workflow.

## 12. Supply-Chain Security

Janavani is polyglot and must secure its entire build chain:

- Rust crates and Cargo lockfiles
- Python packages and lock/constraint mechanisms
- JavaScript/TypeScript packages and lockfiles
- WASM toolchains
- Docker base images and build dependencies
- GitHub Actions and workflow dependencies
- Generated code and generated artifacts
- AI/model/provider dependencies
- Release artifacts

Review dependency vulnerabilities, malicious packages, transitive dependencies, lockfile integrity, workflow pinning, container provenance and unexpected build-time network access.

## 13. Evidence Standard

Each security gate should produce inspectable evidence, for example:

- Tool/test name and version
- Scope and commit SHA
- Findings
- Severity
- Reproduction or verification evidence
- Remediation
- Residual risk/limitation
- Reviewer and date where human review applies

A green check without knowing what was actually checked is not sufficient evidence.

## 14. Implementation Policy

Do not make developers repeatedly paste a large security prompt into every task. Convert security requirements into canonical documentation, automated checks, targeted AI review and human review.

New security ideas discovered during implementation should be documented and parked rather than automatically implemented unless they are required to close a verified current risk or release gate.

## 15. Assurance Limitation

This specification is an assurance framework, not a substitute for professional penetration testing, threat-led testing, independent review, incident response planning or legal/compliance advice where those are required.

## Related Documents

- `docs/security/JANAVANI_THREAT_MODEL.md`
- `docs/security/JANAVANI_DATA_FLOW_SECURITY.md`
- `docs/security/JANAVANI_AI_AGENT_SECURITY.md`
- `docs/security/JANAVANI_EVIDENCE_SECURITY.md`
- `docs/security/JANAVANI_RELEASE_SECURITY_GATE.md`
- `docs/strategy/FUTURE_IDEAS_REGISTER.md`
