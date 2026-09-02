# Canonical Civic Case RLS & Authorization Matrix

**Status:** Design/security contract — implementation pending approval
**Scope:** Authorization and PostgreSQL/Supabase RLS requirements for durable Civic Case storage.
**Important:** This document defines policy intent. It does **not** authorize creation or modification of RLS SQL policies.

## 1. Security principle

Janavani must separate:

```text
Identity
  -> Authentication
      -> Authorization
          -> Purpose / Consent
              -> Data access
```

Authentication alone must never imply access to private case content.

The application/domain authorization layer and database RLS are complementary:

- Domain/service authorization decides whether an operation is lawful and valid in context.
- RLS provides a database-level containment boundary.
- A transport adapter must never bypass the repository/security boundary.

## 2. Case data classes

| Class | Examples | Default exposure |
|---|---|---|
| Public reference | case capability type, aggregate status where explicitly published | Public only when intentionally published |
| Case metadata | case ID, type, status, timestamps | Case principal only by default |
| Private case content | narrative, claims, attachments, document content | Strictly authorized principals |
| Sensitive case content | whistleblower/corruption or other protected material | Dedicated restricted policy boundary |
| Evidence metadata | evidence ID, provenance, hash, storage reference | Authorized case principals/services |
| Evidence bytes | photos, PDFs, recordings | Evidence capability policy; never public by default |
| Consent records | purpose, scope, status, proof reference | Subject/authorized security boundary |
| Delivery records | destination, transport, external reference, acknowledgement | Authorized case principals/services |
| Audit records | actor, action, result, reason | Restricted operator/audit boundary |

## 3. Principal classes

| Principal | Meaning |
|---|---|
| `anonymous` | Unauthenticated/public caller |
| `citizen` | Authenticated or otherwise recognized case principal |
| `delegate` | Explicitly authorized person acting for the case principal |
| `support_operator` | Authorized Janavani support role with limited operational access |
| `destination_service` | Service adapter responsible for a specific submission/delivery operation |
| `government_actor` | Destination-side actor, only when a verified integration/identity model exists |
| `admin` | Privileged operational administrator; access must remain auditable and purpose-bound |
| `system_service` | Backend service using a narrowly scoped service identity |
| `auditor` | Restricted audit/compliance role |

## 4. Operation matrix

Legend:

- **ALLOW** = permitted subject to ordinary validation.
- **CONDITIONAL** = permitted only after additional authorization/consent/purpose checks.
- **DENY** = must not be permitted through ordinary case access.

| Operation | Anonymous | Citizen | Delegate | Support | Destination | Admin | System | Auditor |
|---|---|---|---|---|---|---|---|---|
| Create own case | DENY/limited | ALLOW | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Read own case | DENY | ALLOW | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Edit own draft/review case | DENY | ALLOW | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Add evidence reference | DENY | ALLOW | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Read private evidence metadata | DENY | ALLOW | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Read evidence bytes | DENY | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Read consent record | DENY | ALLOW | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | CONDITIONAL |
| Approve/mark ready | DENY | ALLOW | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Begin/queue submission | DENY | ALLOW | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Mark submitted | DENY | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Record acknowledgement | DENY | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Read delivery status | DENY | ALLOW | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | ALLOW | DENY |
| Close/archive case | DENY | CONDITIONAL | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | DENY |
| Read audit trail | DENY | LIMITED own-case | CONDITIONAL | CONDITIONAL | DENY | CONDITIONAL | ALLOW | ALLOW |

This matrix is intentionally conservative. Exact role grants require threat-model and deployment review.

## 5. Core RLS invariants

### 5.1 Case ownership

A private case row must be readable only when the authenticated principal is the case owner or has an explicitly recorded delegation/authorization relationship, except for narrowly defined support/system/audit roles.

### 5.2 No broad authenticated access

Do **not** implement a policy equivalent to:

```text
authenticated users -> SELECT all civic_cases
```

Authentication is not authorization.

### 5.3 Writes are operation-specific

INSERT, UPDATE, and DELETE/retirement operations require separate policy reasoning. A principal allowed to read a case is not automatically allowed to modify it.

### 5.4 Lifecycle integrity

RLS must not become the only lifecycle control. The service/domain layer must validate legal transitions such as:

```text
DRAFT -> REVIEW -> READY -> SUBMITTING -> QUEUED -> SUBMITTED
                                                   -> ACKNOWLEDGED
```

RLS prevents unauthorized access; it does not replace transition validation.

### 5.5 Consent

Submission and optional data use require valid consent where the canonical contract requires it. RLS cannot by itself establish that consent is valid for the intended purpose.

### 5.6 Sensitive cases

Protected categories must not inherit ordinary case policies blindly. They require explicit policy review, stronger roles, minimized logging, and potentially a separate storage/security boundary.

## 6. Table-specific policy intent

### `civic_cases`

- Citizen: own case only.
- Delegate: cases covered by active delegation.
- Support: limited operational access, purpose-bound and auditable.
- Destination: no general case access; only the minimum submission payload required for an authorized delivery operation.
- Admin: exceptional, audited access.
- System service: narrow service identity, not unrestricted application-wide read/write.
- Anonymous: no private case reads.

### `civic_case_events`

- Citizen/delegate: read events for authorized cases, subject to privacy filtering.
- Ordinary clients: cannot arbitrarily insert lifecycle events.
- System/service: append only through controlled repository/service operations.
- Events should be treated as history; ordinary UPDATE/DELETE should be prohibited or tightly restricted.

### `civic_case_evidence_refs`

- Access follows case authorization plus evidence capability policy.
- A case reference does not itself grant access to the underlying binary.
- Deleting a reference must not silently delete evidence bytes.

### `civic_case_document_refs`

- Access follows case authorization and document capability policy.
- Document content is separately protected.
- Case persistence must not trigger email delivery.

### `civic_case_submissions`

- Citizen/delegate: read their submission status and references.
- Submission service: create/update only records belonging to its authorized operation.
- Destination integration: access only the minimum destination-bound data.
- A local `SUBMITTED` record must not be treated as destination acknowledgement.

### Consent records

- Subject can inspect their own consent state.
- Services may validate consent for an operation.
- Support/admin access is purpose-bound and audited.
- Revocation must take effect for future operations according to the consent contract.

### Audit records

- Append-only semantics wherever technically feasible.
- Read restricted to authorized audit/security roles and relevant system services.
- Ordinary users must not be able to rewrite audit history.

## 7. Service identity rules

Backend service identities must be separated by capability where practical:

```text
case-service
submission-service
identity-service
 evidence-service
document-service
audit-service
```

A service should receive only the database permissions required for its function. Avoid one universal service identity for every subsystem if the deployment model permits finer separation.

## 8. API-to-RLS alignment

The HTTP router currently consumes the repository boundary. It must not receive a database client and issue arbitrary SQL.

Required path:

```text
HTTP / Telegram / Mobile / DApp
        -> adapter
        -> application service
        -> domain authorization + transition validation
        -> repository
        -> database policy enforcement
```

This prevents interface-specific authorization drift.

## 9. Negative security tests required before activation

At minimum, automated tests must prove:

1. Citizen A cannot read Citizen B's private case.
2. Citizen A cannot edit Citizen B's case.
3. A delegate without active authorization cannot access the case.
4. A revoked delegate loses access.
5. Anonymous callers cannot enumerate private cases.
6. A citizen cannot insert a fabricated acknowledgement event.
7. A client cannot modify historical lifecycle events directly.
8. A case reference does not grant unrestricted evidence-byte access.
9. Destination service cannot read unrelated cases.
10. Admin access is auditable.
11. Expired/revoked consent cannot authorize a new submission operation.
12. Submission persistence cannot manufacture government acknowledgement.
13. Cross-tenant/cross-user queries cannot bypass ownership predicates.
14. Stale-version writes are rejected by the repository/database concurrency control.

## 10. Logging and privacy

- Never log full private narratives or evidence bytes.
- Avoid putting tokens, passwords, private contact data, or document bodies into error messages.
- Audit access to sensitive cases without duplicating their sensitive content into logs.
- Hash/reference large sensitive payloads rather than copying them into audit metadata.
- Retention of logs must be separately governed.

## 11. RLS implementation gate

Before any SQL policy is created or changed, the following must be approved/verified:

1. Actual PostgreSQL/Supabase schema and migrations.
2. Authentication identity mapping.
3. Role model and service identities.
4. Delegation model.
5. Consent model.
6. Sensitive-case classification.
7. Data retention/deletion requirements.
8. Backup/recovery implications.
9. Negative-access test plan.
10. Production rollback plan.

**No RLS SQL is implemented by this document.**

## 12. Decision

The canonical design is:

```text
Identity + Authentication
        ↓
Domain Authorization
        ↓
Consent / Purpose Check
        ↓
Repository Contract
        ↓
PostgreSQL RLS
        ↓
Authorized Data
```

The durable Civic Case provider must not be activated until this chain is implemented and failure-tested.
