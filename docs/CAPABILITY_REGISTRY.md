# 🇮🇳 JANAVANI — CAPABILITY REGISTRY

**Status:** CANONICAL DESIGN REGISTER — v1.0
**Date:** 23 August 2026
**Purpose:** Define each Janavani capability as an explicit, testable contract. This registry describes the intended full ecosystem; it does not claim that every capability is currently implemented.

## Status vocabulary

- `ARCHITECTURE LOCKED` — approved in the master architecture.
- `DESIGN` — capability definition is being formalised.
- `IMPLEMENTATION` — code exists or is being built; verify repository state before calling complete.
- `VERIFYING` — implementation exists but completion gates are not satisfied.
- `COMPLETE` — implementation, tests, verification and documentation satisfy the master checklist.
- `ARCHIVED` — superseded material retained for historical/recovery purposes.

## Contract fields

Each capability is defined by:

- ID
- Purpose
- Primary actor
- Permission/consent
- Identity requirement
- AI dependency
- Offline/local support
- Supported channels
- Supported transports
- Inputs
- Outputs
- Evidence/provenance
- Failure behavior
- Completion tests
- Current status

---

# A. CIVIC ACCESS

## JNV-CIVIC-COMPLAINT
**Purpose:** Structure and prepare a citizen complaint against an office, service, official action or other reportable matter.

- Actor: Citizen
- Permission: User submission consent
- Identity: Optional depending on destination requirement
- AI: Optional
- Offline: Drafting where local capability exists
- Channels: Web, Android, iOS, Telegram, Mini App, WhatsApp, Messenger, DApp where supported
- Transports: Internet; local/offline queue where supported
- Inputs: Citizen narrative, office, incident, date, supporting evidence
- Outputs: Structured case + draft complaint + destination information
- Evidence: Source documents and user attachments preserved
- Failure: Save draft; never claim submission without confirmed acknowledgement
- Status: DESIGN

## JNV-CIVIC-GRIEVANCE
**Purpose:** Prepare and track a grievance to the appropriate government mechanism.
- Actor: Citizen
- Permission: Explicit submission consent
- AI: Optional
- Offline: Draft/save where supported
- Outputs: Grievance package, destination, tracking metadata
- Failure: Draft remains available; submission status remains unconfirmed until acknowledgement
- Status: DESIGN

## JNV-CIVIC-RTI
**Purpose:** Assist with RTI application preparation, authority identification and follow-up.
- Actor: Citizen
- Permission: Explicit user approval before submission
- Identity: User controlled; destination requirements apply
- AI: Optional RAG assistance
- Offline: Drafting possible
- Outputs: RTI application, PIO/authority details where verified, first-appeal workflow where applicable
- Evidence: Official source URLs/references and address version
- Failure: Preserve draft and explain unresolved authority/address
- Status: DESIGN

## JNV-CIVIC-PETITION
**Purpose:** Prepare petitions, representations and formal requests.
- Actor: Citizen / organisation
- AI: Optional
- Outputs: Purpose-bound document package
- Status: DESIGN

## JNV-CIVIC-OBJECTION
**Purpose:** Prepare an objection/representation against a notified action or decision.
- AI: Optional
- Evidence: Source notification required where available
- Status: DESIGN

## JNV-CIVIC-APPEAL
**Purpose:** Prepare follow-up/appeal documents using case history and authoritative procedure.
- AI: Optional
- Evidence: Original submission and response/absence of response
- Status: DESIGN

---

# B. GOVERNMENT INFORMATION

## JNV-GOV-OFFICE-SEARCH
**Purpose:** Find relevant government offices and verified contact/address information.
- Actor: Citizen
- Identity: Not required for search
- AI: Optional
- Offline: Cached verified data where available
- Evidence: Source, verification date, version
- Correction: Citizen may propose corrections
- Status: DESIGN

## JNV-GOV-OFFICER-SEARCH
**Purpose:** Identify relevant public officials and role-based contact information where lawfully/publicly available.
- Privacy: Minimise personal data; prefer official role/contact information
- Correction: User-submitted corrections require verification
- Status: DESIGN

## JNV-GOV-SCHEME-SEARCH
**Purpose:** Discover Central and State government schemes, benefits, eligibility and application requirements.
- Actor: Citizen
- AI: Optional RAG
- Evidence: Authoritative government source required
- Outputs: Scheme summary, eligibility, required documents, application route, source date
- Status: DESIGN

## JNV-GOV-SCHEME-ELIGIBILITY
**Purpose:** Help a citizen assess likely eligibility without representing an AI estimate as an official eligibility determination.
- Inputs: User-provided circumstances
- Outputs: Likely eligibility + reasons + official verification route
- AI: Optional
- Status: DESIGN

## JNV-GOV-ALERT-PUBLIC
**Purpose:** Receive and distribute authenticated government emergency alerts.
- Actor: Authorised government source
- Consent: Citizen controls opt-in/opt-out according to product policy and applicable emergency requirements
- AI: Never the authority; optional separate explanation layer
- Evidence: Official provenance, source identity, issue/expiry/update timestamps
- Transports: Internet, mesh and authorised satellite/community gateway
- Failure: Preserve official alert and retry; never fabricate an alert
- Status: ARCHITECTURE LOCKED

---

# C. ACCOUNTABILITY

## JNV-ACCOUNTABILITY-OFFICE-REVIEW
**Purpose:** Collect structured citizen reviews of government office/service experience.
- Actor: Citizen
- Identity: Optional public attribution; platform moderation identity retained only as policy permits
- AI: Optional moderation/analysis
- Evidence: Case references where claims are factual allegations
- Safeguards: Anti-brigading, duplicate detection, abuse controls, right-of-response, allegation/verified-finding distinction
- Status: DESIGN

## JNV-ACCOUNTABILITY-OFFICER-REVIEW
**Purpose:** Structured feedback on public-service experience involving an officer.
- Actor: Citizen
- Privacy: Focus on official conduct/service, not irrelevant personal information
- Safeguards: Defamation, harassment, retaliation and manipulation controls
- Status: DESIGN

## JNV-ACCOUNTABILITY-REPRESENTATIVE-REVIEW
**Purpose:** Structured evaluation of MPs/MLAs using defined public-performance indicators and sourced public information.
- Actor: Citizen / platform analyst
- Evidence: Public records and clearly labelled citizen experience
- Safeguards: Distinguish opinion, allegation, sourced fact and verified finding
- Status: DESIGN

## JNV-ACCOUNTABILITY-GOV-PERFORMANCE
**Purpose:** Aggregate transparent indicators for Central and State government performance.
- Actor: Public / analysts
- AI: Optional analytical layer
- Evidence: Source-linked datasets and methodology
- Status: DESIGN

## JNV-ACCOUNTABILITY-TRANSFER-CONCERN
**Purpose:** Allow citizens to report concern when a good-performing officer appears to have been transferred before an applicable minimum/tenure period without a publicly stated valid reason.
- Actor: Citizen / community
- Evidence: Transfer order, applicable tenure policy/rule, service record where lawfully available
- Outputs: Structured concern + representation to relevant department/administrative head and elected representatives where appropriate
- Safeguards: No presumption that every early transfer is unlawful or improper; classify as concern pending evidence
- Status: DESIGN

## JNV-ACCOUNTABILITY-MISBEHAVIOUR
**Purpose:** Report alleged disrespectful, abusive or improper conduct by public personnel.
- Evidence: Date, location, office, witnesses, documents/recordings where lawfully obtained
- Safeguards: Allegation is not treated as established fact
- Status: DESIGN

## JNV-ACCOUNTABILITY-CORRUPTION
**Purpose:** Structure corruption allegations and route them to appropriate complaint/oversight mechanisms.
- Evidence: Required/optional depending on safe reporting circumstances
- Security: High-risk handling; may link to whistleblower workflow
- Status: DESIGN

---

# D. DOCUMENT & ADDRESS INTELLIGENCE

## JNV-DOC-GENERATE
**Purpose:** Generate purpose-bound civic documents.
- Outputs: PDF and DOCX
- Address: Full postal address + email for To and CC where verified/available
- User control: User can edit/correct addresses before export
- AI: Optional
- Status: DESIGN

## JNV-DOC-ADDRESS-CORRECTION
**Purpose:** Let users correct government address/contact data and submit the proposed correction to JanaVani.
- Inputs: Existing record, proposed correction, evidence
- Outputs: Candidate correction + audit trail
- Verification: Source comparison / expert review / official confirmation
- Gamification: Only rewards verified accuracy
- Status: DESIGN

## JNV-DOC-EXPORT
**Purpose:** Export approved draft to PDF/DOCX.
- Status: DESIGN

---

# E. EVIDENCE & PROVENANCE

## JNV-EVIDENCE-CAPTURE
**Purpose:** Capture user-provided documents, images, audio, video and structured facts.
- Privacy: Explicit consent and minimisation
- Integrity: Hash/provenance metadata
- Offline: Capture locally where supported
- Status: DESIGN

## JNV-EVIDENCE-PROVENANCE
**Purpose:** Preserve source, timestamp, transformation and chain-of-custody metadata.
- AI: Not required
- Status: DESIGN

## JNV-EVIDENCE-BLOCKCHAIN-ANCHOR
**Purpose:** Optionally anchor evidence hashes/provenance proofs to an authorised blockchain.
- Critical dependency: No
- Original evidence remains retrievable through approved storage/archives
- Failure: Continue normal operation if blockchain is unavailable
- Status: ARCHITECTURE DEFINED

## JNV-EVIDENCE-ARCHIVE
**Purpose:** Retain superseded material under an explicit retention policy rather than deleting it merely because it is old.
- Exceptions: Privacy/legal deletion requirements
- Status: ARCHITECTURE LOCKED

---

# F. WHISTLEBLOWER

## JNV-WB-SUBMIT
**Purpose:** Securely submit high-risk wrongdoing concerns.
- Actor: Citizen / insider / witness
- Identity: User chooses supported anonymity/pseudonymity model
- AI: Not required for submission
- Security: Encryption, metadata minimisation, strict reviewer permissions
- Evidence: Optional attachment with integrity metadata
- Failure: Local encrypted queue where feasible; never falsely claim delivery
- Status: DESIGN

## JNV-WB-CASE
**Purpose:** Manage a whistleblower case through controlled reviewers and escalation.
- Access: Need-to-know
- Audit: Access and action logging
- Status: DESIGN

---

# G. EXPERT / VOLUNTEER / NGO NETWORK

## JNV-EXPERT-REGISTER
**Purpose:** Optional registration of subject experts, individuals, societies, communities, NGOs and institutions.
- Actor: Participant
- Permission: Explicit registration
- Verification: Tiered, evidence-based
- Conflict of interest: Required where applicable
- Status: DESIGN

## JNV-EXPERT-REVIEW
**Purpose:** Assign qualified reviewers to data corrections, evidence interpretation or subject-specific review.
- AI: Optional support, never automatic authority
- Status: DESIGN

## JNV-CONTRIBUTION-REPUTATION
**Purpose:** Measure contribution quality without allowing gamification to override evidence quality.
- Status: DESIGN

---

# H. AI / KNOWLEDGE

## JNV-AI-OCR
**Purpose:** OCR for citizen documents and government records.
- Offline/local: Preferred where feasible
- Status: DESIGN

## JNV-AI-VISION
**Purpose:** Computer vision/document understanding for permitted civic workflows.
- Status: DESIGN

## JNV-AI-RAG
**Purpose:** Retrieve grounded information from authoritative and versioned sources.
- Output: Source citations and source date/version
- Failure: Say source unavailable rather than inventing an answer
- Status: DESIGN

## JNV-AI-SLM
**Purpose:** Local/small-model inference for privacy, offline and low-resource workflows.
- Status: DESIGN

## JNV-AI-LLM
**Purpose:** Higher-capability language reasoning for approved tasks.
- Provider abstraction required
- Status: DESIGN

## JNV-AI-AGENT
**Purpose:** Execute approved multi-step workflows using explicit tools and permissions.
- Human approval gates required for consequential external actions
- Status: DESIGN

---

# I. SOS

## JNV-SOS-PERSONAL
**Purpose:** Citizen-triggered emergency SOS.
- Actor: Citizen
- Consent: User-configured recipients and escalation policy
- Identity: User-controlled subject to emergency destination requirements
- AI: Not required
- Offline: Yes — queue/store-and-forward
- Channels: Native apps and other supported channels
- Transports: Internet, mesh, satellite, local relay
- Inputs: Severity/category, optional message, location if user permits, recipients
- Outputs: SOS packet + delivery state
- Failure: Secure queue/retry; never report delivery without acknowledgement
- Status: ARCHITECTURE LOCKED

## JNV-SOS-SILENT
**Purpose:** Trigger SOS discreetly without requiring a visible conversation flow.
- Status: ARCHITECTURE LOCKED

## JNV-SOS-MESH
**Purpose:** Deliver SOS over local/community mesh when conventional Internet is unavailable.
- Transports: Reticulum, LoRa/RNode, Meshtastic and compatible future adapters
- Multi-hop: Required
- Store-and-forward: Required
- Status: ARCHITECTURE LOCKED

## JNV-SOS-SATELLITE
**Purpose:** Deliver SOS through supported, legally authorised satellite transport.
- Provider abstraction: Required
- Native device satellite: Adapter
- Companion communicator: Adapter
- Community gateway: Architecture supported
- India compliance: Required before deployment of a particular service/device
- Status: ARCHITECTURE LOCKED

## JNV-SOS-ROUTER
**Purpose:** Select one or multiple available transports based on configured emergency policy and transport health.
- States: Available/degraded/unavailable/not configured
- Multi-path: Supported
- Status: ARCHITECTURE LOCKED

## JNV-SOS-DELIVERY
**Purpose:** Provide truthful delivery status.
- State machine: CREATED → QUEUED → TRANSMITTING → SENT → RECEIVED → ACKNOWLEDGED
- Status: ARCHITECTURE LOCKED

---

# J. FINANCIAL TRANSPARENCY

## JNV-FIN-EXPENDITURE
**Purpose:** Show operating expenditure by category/head with current reporting period and source/accounting basis.
- Status: DESIGN

## JNV-FIN-CONTRIBUTE
**Purpose:** Allow voluntary financial contribution through authorised mechanisms.
- Status: DESIGN

## JNV-FIN-CONTRIBUTOR-DISPLAY
**Purpose:** Let contributor choose public display format.
- Options: name only; name + photo; name + photo + amount; anonymous + amount; private/not publicly displayed
- Full disclosure: Governed by applicable law, privacy and financial compliance requirements
- Status: DESIGN

## JNV-FIN-RESERVE
**Purpose:** Maintain an operating reserve under transparent governance rules.
- Recommendation: Do not hard-code exactly three months as an immutable rule; use a board-approved risk-based reserve target, publish the policy and report actual reserve coverage.
- Status: DESIGN

---

# K. CHANNELS

## JNV-CHANNEL-WEB
Dynamic web application consuming capability APIs.
- Status: DESIGN

## JNV-CHANNEL-ANDROID
Native Android client.
- Status: DESIGN

## JNV-CHANNEL-IOS
Native iOS client.
- Status: DESIGN

## JNV-CHANNEL-TELEGRAM
Telegram Bot and Mini App adapters.
- Status: DESIGN

## JNV-CHANNEL-WHATSAPP
WhatsApp integration adapter.
- Status: DESIGN

## JNV-CHANNEL-MESSENGER
Messenger integration adapter.
- Status: DESIGN

## JNV-CHANNEL-DAPP
Web3 DApp interface.
- Status: DESIGN

---

# L. TRANSPORTS

## JNV-TRANSPORT-INTERNET
Cellular/Wi-Fi Internet transport.
- Status: DESIGN

## JNV-TRANSPORT-MESH
Mesh transport abstraction.
- Adapters: Reticulum, LoRa/RNode, Meshtastic as supported
- Status: ARCHITECTURE LOCKED

## JNV-TRANSPORT-SATELLITE
Satellite transport abstraction.
- Provider/device independent
- India regulatory verification required
- Status: ARCHITECTURE LOCKED

## JNV-TRANSPORT-LOCAL
Bluetooth/Wi-Fi Direct/local store-and-forward where supported.
- Status: DESIGN

## JNV-TRANSPORT-FREENET
Optional decentralized transport/storage integration.
- Critical dependency: No
- Status: DESIGN

---

# M. CROSS-CAPABILITY RULES

1. **User choice:** Access, identity linking, public attribution and optional features are user-controlled unless law/safety requirements require otherwise.
2. **No false success:** Attempted transmission is not delivery.
3. **No false authority:** AI output is not an official government determination.
4. **Evidence distinction:** allegation, opinion, sourced fact and verified finding must remain distinct.
5. **Source traceability:** Government information should retain source identity, date/version and verification state.
6. **Failure isolation:** Failure of an external provider must not break unrelated capabilities.
7. **Offline honesty:** Local operation may store, process or prepare; it cannot claim remote delivery without a communication path.
8. **Archive before deletion:** Preserve recoverable history unless privacy, legal, retention or security rules require deletion.
9. **Privacy by purpose:** Collect only data necessary for the declared capability.
10. **Human review:** Consequential actions require appropriate human confirmation.
11. **Provider independence:** AI, cloud, messaging, satellite, blockchain and decentralized providers must be replaceable through adapters.
12. **Verification before completion:** Capability status is promoted to COMPLETE only through the master checklist completion gate.

---

# N. IMPLEMENTATION PRIORITY

1. Capability registry and contracts
2. Data contracts
3. Repository audit/reconciliation
4. Identity/permission/evidence foundations
5. Civic document + government information foundations
6. Accountability and whistleblower foundations
7. SOS + resilient transport
8. Distributed/Web3 capabilities
9. Full multi-channel clients
10. Full-scale field testing and operational certification

**END — CAPABILITY REGISTRY**
