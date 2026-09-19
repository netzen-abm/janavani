# Janavani Supabase Free-Tier Operating Boundary

**Status:** CANONICAL OPERATING CONSTRAINT

## Decision
For the current Janavani phase, Supabase will remain at the minimum practical footprint on the free service. This is an infrastructure constraint, not an architectural dependency.

Janavani must remain portable to another PostgreSQL-compatible provider without redesigning its domain/capability contracts.

## Supabase may provide
Initially only the minimum services actually required:
- PostgreSQL database;
- Supabase Auth only if the identity implementation explicitly selects it;
- Storage only if required after the artifact boundary is defined.

Other Supabase features remain optional and must not become implicit dependencies.

## Explicit non-dependencies
Do not make Janavani dependent on paid Supabase features, Realtime merely because it exists, Edge Functions merely because they exist, pgvector for core Civic Case persistence, Vault for citizen credentials, or Supabase-specific client access as the only application path.

## Free-tier principles
Treat the service as capacity-constrained and replaceable. Do not assume unlimited database size, compute, bandwidth, storage, logs, or function execution.

## Data policy
Store only what the MVP requires. Relational case metadata may reside in PostgreSQL; large evidence/document binaries should remain outside ordinary case rows; sensitive data must be minimized; credentials and access/refresh tokens do not belong in Civic Case records; AI agents never receive unrestricted database credentials.

## Production safety
Free tier does not relax security. RLS, authorization, least privilege, transaction integrity, auditability and privacy remain mandatory before citizen production data is exposed.

## Provider portability
The dependency direction remains:

Capability → Repository Contract → Provider

not:

Capability → Supabase

## Upgrade trigger
Consider paid tier or another provider only when measured requirements exceed the free boundary, such as sustained traffic/storage/compute, reliability/recovery requirements, backup/PITR needs, observability, quotas, or security/compliance requirements.

## Current conclusion
Supabase free tier is acceptable as minimal development/MVP infrastructure provided the security and transaction gates are satisfied before real citizen data is exposed.
