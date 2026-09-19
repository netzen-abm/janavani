# Janavani Civic Case Authorization Matrix

**Status:** CANONICAL SECURITY DESIGN — implementation gate
**Version:** 1.0

## Purpose
Define the authorization inputs and access classes required before PostgreSQL/Supabase RLS is enabled for Civic Case data.

This is an authorization contract, not an RLS implementation.

## Core rule
Authentication identifies the authenticated principal. Authorization determines what that principal may do to a specific resource in context. Consent remains a separate purpose/scope boundary.

No Telegram, WhatsApp, Web, Android, iOS, DApp or other channel identifier is a canonical authorization identity.

## Access classes
| Principal | Own case | Delegated case | Other citizen case | Sensitive case | Admin/system |
|---|---|---|---|---|---|
| Citizen | ownership policy | explicit active grant | deny | explicit policy/step-up | deny |
| Delegate | only if owner too | grant scope | deny | grant + elevated policy | deny |
| Support/operator | controlled scope | controlled scope | deny by default | separate elevated scope | deny |
| Destination/external service | no general access | no general access | deny | deny by default | no |
| Janavani system service | capability-scoped | capability-scoped | deny by default | capability-specific | explicit scope |
| Administrator | controlled audited scope | controlled audited scope | controlled audited scope | separate audited scope | controlled |
| Anonymous/pseudonymous | only where capability permits | deny | deny | deny | deny |

## Operation rules
- created_by resolves to the Janavani-owned opaque identity, never a channel identifier.
- Anonymous creation is permitted only for explicitly approved workflows with a defined continuation/ownership model.
- Updates require ownership, delegation, or approved support scope and must pass lifecycle validation.
- Historical case events are append-oriented; ordinary clients cannot update or delete them.
- Evidence/document references follow case authorization; a case reference does not grant unrestricted artifact access.
- Consent records remain capability-owned. Ownership does not imply consent.
- Submission access follows the case and submission capability. Local submission state never proves external acknowledgement.
- Delete/anonymize is a capability workflow governed by retention, legal hold, audit and privacy rules, not generic client row deletion.

## Delegation
Delegation must be explicit, scoped, revocable, auditable and purpose-limited. It must not grant unrestricted account access, credentials, all cases, all evidence, or administrative privileges.

## Sensitive cases
Sensitive case classes require separate policy. Ordinary case ownership is not automatically sufficient for every sensitive operation. Stronger authentication, narrower delegation, explicit confirmation or elevated audited support may be required according to the relevant capability contract.

## System/service access
System services are not citizens. Each service receives only data required for its declared capability and purpose. AI/agent services never receive unrestricted database credentials.

## Database mapping
The target model is:

Janavani Principal → Policy Decision → database role/context → RLS predicate

RLS is defense-in-depth; service-layer authorization remains authoritative for workflow decisions.

## RLS activation gate
Before enabling production RLS, demonstrate:
1. canonical identity mapping;
2. verified ownership predicate;
3. verified delegation predicate;
4. verified service/system scopes;
5. verified anonymous behavior;
6. sensitive-case policy;
7. event immutability;
8. submission access;
9. cross-user denial tests;
10. policy-performance indexes;
11. rollback/recovery.

## Required tests
At minimum:
- citizen A cannot read/update citizen B's case;
- citizen A cannot insert events into citizen B's case;
- expired/revoked delegate cannot access delegated case;
- delegate cannot exceed grant scope;
- anonymous caller cannot enumerate cases;
- support operator cannot access unrelated cases;
- service cannot read unrelated cases;
- historical events cannot be changed through ordinary client access;
- consent-dependent operation fails after revocation;
- sensitive access follows elevated policy;
- administrator access is separately audited.

## Non-goals
This contract does not enable RLS, create SQL policies, create an authentication provider, store passwords/tokens, authorize external government services, make Supabase mandatory, or require paid Supabase features.
