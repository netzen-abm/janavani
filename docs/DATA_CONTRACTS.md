# 🇮🇳 JANAVANI — DATA CONTRACTS

**Status:** CANONICAL DESIGN REGISTER — v1.0
**Date:** 23 August 2026
**Purpose:** Define the canonical data objects shared across Janavani capabilities and channels. These are design contracts, not claims that every object is already implemented.

## 0. Contract principles

1. Every object has a stable identifier.
2. Every externally sourced fact has provenance where practical.
3. Every user-generated claim is distinguishable from a verified fact.
4. Consent is explicit for optional data uses.
5. Sensitive data is minimised.
6. Timestamps use UTC internally and preserve the user's local timezone for display where needed.
7. Versioning is mandatory for schemas and important source records.
8. Deletion is governed by retention/privacy/legal requirements; archival is preferred for superseded material where lawful.
9. No capability may infer successful external delivery from local persistence alone.
10. Cross-channel systems exchange capability contracts, not channel-specific internal objects.

---

# 1. COMMON TYPES

## 1.1 `EntityId`

```text
id: string              # globally unique opaque identifier
entity_type: string
version: integer
created_at: datetime
updated_at: datetime
```

IDs must not encode unnecessary personal information.

## 1.2 `SourceRef`

```text
source_id: string
source_type: OFFICIAL | USER | EXPERT | INSTITUTION | PUBLIC_RECORD | OTHER
publisher: string|null
title: string|null
uri: string|null
retrieved_at: datetime|null
published_at: datetime|null
version_or_reference: string|null
verification_status: UNVERIFIED | CANDIDATE | VERIFIED | REVOKED
verification_method: string|null
```

## 1.3 `Claim`

```text
claim_id: string
statement: string
claim_type: OPINION | ALLEGATION | USER_REPORT | SOURCED_FACT | VERIFIED_FINDING
source_refs: SourceRef[]
reported_by: EntityId|null
reported_at: datetime
status: ACTIVE | DISPUTED | CORRECTED | WITHDRAWN | ARCHIVED
```

A citizen rating or complaint must never silently become a `VERIFIED_FINDING`.

## 1.4 `Consent`

```text
consent_id: string
subject_id: EntityId
purpose: string
scope: string[]
grant_type: EXPLICIT | REQUIRED_BY_DESTINATION | NOT_REQUIRED
status: GRANTED | DENIED | REVOKED | EXPIRED
created_at: datetime
expires_at: datetime|null
revoked_at: datetime|null
proof_ref: string|null
```

## 1.5 `AuditEvent`

```text
event_id: string
actor_id: EntityId|null
action: string
object_type: string
object_id: string
occurred_at: datetime
result: SUCCESS | FAILURE | PARTIAL
reason: string|null
source_channel: string|null
metadata_hash: string|null
```

---

# 2. USER / IDENTITY

## 2.1 `UserProfile`

```text
user_id: EntityId
preferred_language: string           # default: en
country: string|null
region: string|null
contact_methods: ContactMethod[]
identity_status: ANONYMOUS | PSEUDONYMOUS | VERIFIED
preferences: UserPreferences
created_at: datetime
updated_at: datetime
```

Do not store a real-world identity merely because a user accesses a public information capability.

## 2.2 `UserPreferences`

```text
public_contributor_display: PRIVATE | NAME | NAME_PHOTO | NAME_PHOTO_AMOUNT | ANONYMOUS_AMOUNT
emergency_alerts: OPT_IN | OPT_OUT
location_sharing: NEVER | ASK_EACH_TIME | PRECONFIGURED_FOR_SOS
analytics_consent: GRANTED | DENIED
cross_channel_linking: GRANTED | DENIED
```

Emergency safety behavior must additionally comply with applicable platform and law requirements.

## 2.3 `ContactMethod`

```text
contact_id: string
kind: EMAIL | PHONE | TELEGRAM | WHATSAPP | MESSENGER | OTHER
value_ref: string
verified: boolean
purpose: string[]
```

Sensitive contact values should be encrypted/protected and should not be exposed through ordinary public APIs.

---

# 3. GOVERNMENT ORGANISATION

## 3.1 `GovernmentOrganisation`

```text
organisation_id: EntityId
name: LocalisedText
level: CENTRAL | STATE | DISTRICT | LOCAL | OTHER
parent_id: EntityId|null
jurisdiction: Jurisdiction
official_domains: string[]
source_refs: SourceRef[]
verification_status: UNVERIFIED | CANDIDATE | VERIFIED | ARCHIVED
valid_from: date|null
valid_to: date|null
```

## 3.2 `GovernmentOffice`

```text
office_id: EntityId
organisation_id: EntityId
name: LocalisedText
office_type: string
jurisdiction: Jurisdiction
postal_address: PostalAddress[]
email_addresses: ContactPoint[]
phone_numbers: ContactPoint[]
official_urls: string[]
hours: string|null
source_refs: SourceRef[]
verification_status: string
last_verified_at: datetime|null
```

Multiple addresses/contact points may exist. Never assume one address is universally correct.

## 3.3 `GovernmentOfficial`

```text
official_id: EntityId
name: LocalisedText
role_title: LocalisedText
organisation_id: EntityId|null
office_id: EntityId|null
official_contact_points: ContactPoint[]
service_start: date|null
service_end: date|null
source_refs: SourceRef[]
verification_status: string
```

Only necessary public/professional information should be stored. Private residential or unrelated personal information is outside this contract.

## 3.4 `ElectedRepresentative`

```text
representative_id: EntityId
name: LocalisedText
position: MP | MLA | OTHER
constituency: string
state_or_union_territory: string
term_start: date|null
term_end: date|null
official_contact_points: ContactPoint[]
source_refs: SourceRef[]
verification_status: string
```

---

# 4. ADDRESS / CONTACT CORRECTIONS

## 4.1 `AddressCorrection`

```text
correction_id: EntityId
object_type: OFFICE | OFFICIAL | DEPARTMENT | AUTHORITY
object_id: string
submitted_by: EntityId|null
current_value: PostalAddress | ContactPoint | object
proposed_value: PostalAddress | ContactPoint | object
reason: string
supporting_evidence: EvidenceRef[]
submitted_at: datetime
status: CANDIDATE | UNDER_REVIEW | ACCEPTED | REJECTED | DUPLICATE
review_events: AuditEvent[]
```

A user correction is a **candidate change** until verified.

---

# 5. CASE / COMPLAINT / GRIEVANCE

## 5.1 `Case`

```text
case_id: EntityId
case_type: COMPLAINT | GRIEVANCE | RTI | PETITION | REPRESENTATION | OBJECTION | APPEAL | CORRUPTION | MISBEHAVIOUR | TRANSFER_CONCERN | OTHER
created_by: EntityId|null
subject: string
narrative: string
jurisdiction: Jurisdiction
related_organisation_id: string|null
related_office_id: string|null
related_official_id: string|null
related_representative_id: string|null
claims: Claim[]
evidence_refs: EvidenceRef[]
document_refs: DocumentRef[]
consent_refs: string[]
status: DRAFT | READY | SUBMITTED | ACKNOWLEDGED | IN_PROGRESS | RESPONDED | ESCALATED | CLOSED | ARCHIVED
created_at: datetime
updated_at: datetime
```

## 5.2 `CaseEvent`

```text
event_id: EntityId
case_id: string
event_type: CREATED | EDITED | EVIDENCE_ADDED | SUBMITTED | ACKNOWLEDGED | RESPONSE | ESCALATED | CORRECTION | CLOSED | ARCHIVED
actor_id: EntityId|null
occurred_at: datetime
source_channel: string|null
source_ref: SourceRef|null
notes: string|null
```

---

# 6. RTI

## 6.1 `RTIRequest`

```text
rti_id: EntityId
case_id: string
applicant_identity_ref: string|null
public_authority_id: string|null
pio_contact_ref: string|null
questions: string[]
fee_information: string|null
delivery_method: string|null
first_appeal_deadline: date|null
source_refs: SourceRef[]
status: DRAFT | READY | SUBMITTED | ACKNOWLEDGED | RESPONSE_RECEIVED | FIRST_APPEAL | CLOSED
```

The destination address/email must be sourced and versioned where available.

---

# 7. GOVERNMENT SCHEMES / BENEFITS

## 7.1 `GovernmentScheme`

```text
scheme_id: EntityId
name: LocalisedText
level: CENTRAL | STATE | LOCAL | OTHER
ministry_or_department_id: string|null
purpose: LocalisedText
eligibility_rules: Rule[]
benefits: Benefit[]
required_documents: DocumentRequirement[]
application_channels: ApplicationChannel[]
official_sources: SourceRef[]
last_verified_at: datetime|null
valid_from: date|null
valid_to: date|null
status: ACTIVE | PAUSED | CLOSED | ARCHIVED | UNVERIFIED
```

## 7.2 `EligibilityAssessment`

```text
assessment_id: EntityId
scheme_id: string
user_id: EntityId|null
inputs: InputField[]
result: LIKELY_ELIGIBLE | LIKELY_NOT_ELIGIBLE | INSUFFICIENT_INFORMATION | UNKNOWN
reasons: string[]
official_verification_required: boolean
source_refs: SourceRef[]
created_at: datetime
```

AI-assisted eligibility is advisory unless the official system itself confirms eligibility.

---

# 8. RATINGS / PERFORMANCE

## 8.1 `ServiceReview`

```text
review_id: EntityId
reviewer_id: EntityId|null
subject_type: OFFICE | OFFICIAL | DEPARTMENT | REPRESENTATIVE | SERVICE
subject_id: string
interaction_date: date|null
service_categories: RatingDimension[]
overall_rating: integer
narrative: string|null
claim_refs: string[]
evidence_refs: EvidenceRef[]
public_display: PRIVATE | PUBLISHED
moderation_status: PENDING | PUBLISHED | LIMITED | REMOVED | DISPUTED | ARCHIVED
right_of_response_ref: string|null
created_at: datetime
```

Ratings are experiential/user-generated unless separately verified.

## 8.2 `PerformanceIndicator`

```text
indicator_id: string
subject_type: OFFICE | OFFICIAL | DEPARTMENT | REPRESENTATIVE | GOVERNMENT
subject_id: string
metric: string
value: number|string
unit: string|null
period_start: date
period_end: date
methodology_ref: SourceRef|null
source_refs: SourceRef[]
verification_status: string
```

Aggregated performance scores must expose methodology and underlying source categories.

---

# 9. TRANSFER CONCERN

## 9.1 `TransferConcern`

```text
transfer_concern_id: EntityId
official_id: string
transfer_order_ref: EvidenceRef|null
previous_posting: string|null
new_posting: string|null
transfer_date: date|null
applicable_tenure_rule_ref: SourceRef|null
reported_reason: string|null
concern_narrative: string
claims: Claim[]
evidence_refs: EvidenceRef[]
requested_actions: string[]
status: DRAFT | SUBMITTED | UNDER_REVIEW | RESPONDED | CLOSED | ARCHIVED
```

The object records a concern; it does not establish wrongdoing merely because a transfer occurred early.

---

# 10. WHISTLEBLOWER

## 10.1 `WhistleblowerSubmission`

```text
submission_id: EntityId
identity_mode: ANONYMOUS | PSEUDONYMOUS | IDENTIFIED
secure_contact_ref: string|null
subject_category: string
narrative: string
evidence_refs: EvidenceRef[]
risk_level: LOW | MEDIUM | HIGH | CRITICAL
retaliation_concern: boolean
consent_scope: string[]
access_policy_ref: string
status: RECEIVED | TRIAGE | REVIEW | ESCALATED | CLOSED | ARCHIVED
created_at: datetime
```

The platform must minimise identifying metadata and strictly control reviewer access.

---

# 11. EXPERT / VOLUNTEER / NGO

## 11.1 `ContributorProfile`

```text
contributor_id: EntityId
participant_type: INDIVIDUAL | EXPERT | SOCIETY | COMMUNITY | NGO | INSTITUTION | OTHER
public_name: string|null
photo_ref: string|null
domains: string[]
credentials_refs: SourceRef[]
verification_level: UNVERIFIED | BASIC | VERIFIED | INSTITUTION_VERIFIED
conflict_of_interest: string|null
public_display: PRIVATE | PUBLIC
status: ACTIVE | SUSPENDED | ARCHIVED
```

## 11.2 `ReviewAssignment`

```text
assignment_id: EntityId
object_type: CORRECTION | EVIDENCE | SCHEME | SOURCE | CASE | OTHER
object_id: string
assigned_to: EntityId
role: REVIEWER | EXPERT | MODERATOR | VERIFIER
assigned_at: datetime
due_at: datetime|null
status: ASSIGNED | ACCEPTED | COMPLETED | DECLINED | REASSIGNED
```

---

# 12. DOCUMENTS

## 12.1 `Document`

```text
document_id: EntityId
document_type: COMPLAINT | GRIEVANCE | RTI | PETITION | REPRESENTATION | OBJECTION | APPEAL | WHISTLEBLOWER | OTHER
title: string
language: string
from_party: PartyRef|null
to_party: PartyRef
cc_parties: PartyRef[]
subject: string
body: string
references: SourceRef[]
enclosures: EvidenceRef[]
version: integer
status: DRAFT | USER_APPROVED | EXPORTED | SUBMITTED | ARCHIVED
```

## 12.2 `PartyRef`

```text
party_type: PERSON | OFFICE | DEPARTMENT | AUTHORITY | REPRESENTATIVE | OTHER
name: string
postal_address: PostalAddress|null
email: string|null
phone: string|null
official_source_ref: SourceRef|null
```

User correction is always possible before final export/submission.

---

# 13. EVIDENCE

## 13.1 `EvidenceObject`

```text
evidence_id: EntityId
owner_id: EntityId|null
evidence_type: DOCUMENT | IMAGE | VIDEO | AUDIO | TEXT | OCR | LOCATION | OTHER
storage_ref: string
sha256: string
captured_at: datetime|null
received_at: datetime
location: GeoPoint|null
source_description: string|null
provenance_refs: SourceRef[]
transformation_history: Transformation[]
access_policy_ref: string
retention_policy_ref: string
status: ACTIVE | DISPUTED | ARCHIVED | DELETED
```

Location must not be collected merely because the device can provide it.

## 13.2 `EvidenceRef`

```text
evidence_id: string
relationship: SUPPORTS | CONTRADICTS | ATTACHMENT | SOURCE | OTHER
```

## 13.3 `Transformation`

```text
transformation_id: string
operation: OCR | RESIZE | TRANSCODE | REDACTION | AI_ANALYSIS | OTHER
tool_or_model: string|null
performed_at: datetime
input_hash: string
output_hash: string
operator_id: EntityId|null
```

---

# 14. SOS

## 14.1 `SOSPacket`

```text
sos_id: EntityId
sender_id: EntityId|null
created_at: datetime
severity: ADVISORY | URGENT | EMERGENCY | CRITICAL
category: PERSONAL_SAFETY | MEDICAL | FIRE | NATURAL_DISASTER | ACCIDENT | CRIME | OTHER
message: string|null
location: GeoPoint|null
location_accuracy_m: number|null
location_timestamp: datetime|null
trusted_contact_ids: string[]
authority_destination_refs: string[]
transport_policy_ref: string
priority: integer
expires_at: datetime|null
integrity_hash: string
```

SOS packets must be minimal enough for constrained transports.

## 14.2 `SOSDelivery`

```text
delivery_id: EntityId
sos_id: string
transport: INTERNET | RETICULUM | LORA | MESHTASTIC | SATELLITE | LOCAL | OTHER
adapter_id: string
attempted_at: datetime
state: CREATED | QUEUED | TRANSMITTING | SENT | RECEIVED | ACKNOWLEDGED | FAILED | EXPIRED
ack_ref: string|null
error_code: string|null
retry_count: integer
```

Only `RECEIVED`/`ACKNOWLEDGED` may be represented to users as confirmed delivery, with wording appropriate to the actual acknowledgement.

## 14.3 `SOSPreference`

```text
preference_id: EntityId
user_id: EntityId
trusted_contacts: string[]
authority_policy: NONE | USER_SELECTED | PRECONFIGURED
location_policy: NEVER | ASK | PRECONFIGURED
silent_mode_enabled: boolean
transport_policy: AUTO | USER_SELECTED | MULTI_PATH
```

---

# 15. GOVERNMENT EMERGENCY ALERT

## 15.1 `GovernmentAlert`

```text
alert_id: EntityId
issuer_organisation_id: string
authority_credential_ref: string
alert_type: NATURAL_DISASTER | WEATHER | PUBLIC_SAFETY | HEALTH | OTHER
severity: INFO | WATCH | WARNING | EMERGENCY
headline: LocalisedText
body: LocalisedText
issued_at: datetime
expires_at: datetime|null
affected_area: GeoArea
source_ref: SourceRef
signature_ref: string
status: ACTIVE | UPDATED | CANCELLED | EXPIRED
```

AI may explain an alert but cannot change its authoritative meaning.

---

# 16. FINANCE

## 16.1 `ExpenditureRecord`

```text
expense_id: EntityId
period: string
category: string
head: string
description: string
amount: decimal
currency: string
vendor_or_payee_ref: string|null
invoice_ref: string|null
fund_class: OPERATING | RESTRICTED | CAPITAL | OTHER
source_record_ref: SourceRef|null
reported_at: datetime
status: REPORTED | VERIFIED | ADJUSTED | ARCHIVED
```

## 16.2 `Contribution`

```text
contribution_id: EntityId
contributor_id: EntityId|null
amount: decimal
currency: string
received_at: datetime
purpose: GENERAL | RESTRICTED | OTHER
public_display: PRIVATE | NAME | NAME_PHOTO | NAME_PHOTO_AMOUNT | ANONYMOUS_AMOUNT
photo_ref: string|null
payment_reference_hash: string|null
status: PENDING | RECEIVED | REFUNDED | DISPUTED | ARCHIVED
```

Full disclosure must be handled through lawful governance and compliance procedures; the public display preference does not automatically determine what may legally be disclosed to authorities.

## 16.3 `ReserveSnapshot`

```text
snapshot_id: EntityId
as_of: datetime
liquid_reserve: decimal
monthly_operating_burn: decimal
reserve_coverage_months: decimal
policy_target_months: decimal
policy_ref: SourceRef
```

---

# 17. SOURCE / KNOWLEDGE

## 17.1 `KnowledgeRecord`

```text
record_id: EntityId
record_type: LAW | RULE | NOTIFICATION | SCHEME | OFFICE_DATA | GOVERNMENT_DATA | PUBLIC_RECORD | OTHER
title: LocalisedText
content_ref: string
source_refs: SourceRef[]
effective_from: date|null
effective_to: date|null
retrieved_at: datetime
version: string|null
status: ACTIVE | SUPERSEDED | REVOKED | ARCHIVED
```

## 17.2 `RAGCitation`

```text
citation_id: string
knowledge_record_id: string
passage_ref: string|null
source_ref: SourceRef
relevance_score: number|null
```

A RAG answer should retain enough citation metadata for a user to understand where the answer came from.

---

# 18. CHANNEL / TRANSPORT

## 18.1 `ChannelEnvelope`

```text
envelope_id: EntityId
channel: WEB | ANDROID | IOS | TELEGRAM | TELEGRAM_MINIAPP | WHATSAPP | MESSENGER | DAPP | API | LOCAL
capability_id: string
actor_id: EntityId|null
payload_ref: string
created_at: datetime
idempotency_key: string
```

## 18.2 `TransportStatus`

```text
transport_id: string
transport_type: INTERNET | MESH | SATELLITE | LOCAL | FRENET | OTHER
state: AVAILABLE | DEGRADED | UNAVAILABLE | NOT_CONFIGURED
last_checked_at: datetime
reason: string|null
```

---

# 19. ARCHIVE / RETENTION

## 19.1 `ArchiveRecord`

```text
archive_id: EntityId
object_type: string
object_id: string
archived_at: datetime
reason: SUPERSEDED | CLOSED | RETENTION | LEGAL_HOLD | PRIVACY | SECURITY | OTHER
previous_version: string|null
archive_storage_ref: string
integrity_hash: string
retention_until: datetime|null
```

Archiving does not mean public publication. Access remains controlled by the object's permission policy.

---

# 20. VERSIONING & MIGRATION

All canonical contracts must carry:

```text
schema_name
schema_version
created_at
updated_at
```

Breaking changes require:

1. new schema version;
2. migration plan;
3. compatibility assessment;
4. tests;
5. change-log entry;
6. archive of superseded contract where appropriate.

---

# 21. CROSS-CONTRACT RULES

### Rule 1 — User report ≠ fact
A citizen complaint, rating or allegation is stored as a report/claim until independently verified.

### Rule 2 — Source provenance travels with information
When government information is displayed, the relevant source and verification state should remain available.

### Rule 3 — Evidence is immutable by reference
If an evidence object is transformed, the original hash/reference and transformation history remain linked.

### Rule 4 — Delivery is independently recorded
A message may be locally stored without being remotely delivered.

### Rule 5 — AI cannot silently alter authoritative records
AI may propose a change; an authorised workflow must approve it.

### Rule 6 — Consent is purpose-bound
Consent for one capability does not automatically grant permission for unrelated capabilities.

### Rule 7 — Cross-channel identity is opt-in
Using multiple JanaVani channels does not automatically create a unified identity profile.

### Rule 8 — Public display is separate from internal accountability
A contributor can choose a public display format while the platform retains only information it is lawfully entitled/required to retain.

### Rule 9 — Archive is not deletion
Superseded records are archived where appropriate. Privacy/legal/security requirements can require controlled deletion.

### Rule 10 — Critical paths avoid optional infrastructure
Blockchain, Freenet, external AI, third-party messaging, and particular satellite providers are adapters, not universal dependencies.

---

# 22. IMPLEMENTATION GATE

Before implementing a database schema or API from these contracts:

- [ ] Compare with actual repository models and storage.
- [ ] Identify existing fields that must be preserved.
- [ ] Identify migrations.
- [ ] Identify sensitive fields.
- [ ] Define validation rules.
- [ ] Define indexes/query patterns.
- [ ] Define retention policy.
- [ ] Define access-control policy.
- [ ] Define test fixtures.
- [ ] Update `MASTER_TASK_CHECKLIST.md`.

**END — DATA CONTRACTS**
