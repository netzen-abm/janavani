# Janavani — Provider Platform Strategy

**Status:** ACTIVE ARCHITECTURAL GUIDANCE  
**Scope:** Full Janavani product/ecosystem  
**Decision horizon:** Re-evaluate providers at production-readiness gate; do not make today's free-tier availability a permanent architecture constraint.

## Executive decision

Janavani should remain **provider-neutral at the domain and capability layers** and use different providers where each is strongest.

### Target production allocation

| Concern | Preferred provider | Role |
|---|---|---|
| Canonical domain/runtime | Janavani-owned Rust code | Source of truth; never provider-owned |
| Edge/DNS/CDN/WAF | Cloudflare | Edge, protection, routing and caching |
| Public WebApp/frontend delivery | Vercel | Web surface and deployment previews |
| Production API/services | Google Cloud Run | Containerized canonical services |
| Production relational persistence | Google Cloud SQL PostgreSQL | Canonical transactional persistence |
| Evidence/document blobs | Google Cloud Storage | Durable artifact/object storage |
| Async/event infrastructure | Google Pub/Sub + Cloud Run Jobs | Decoupled workflows and workers |
| Scheduled work | Google Cloud Scheduler | Scheduled capability execution |
| Secrets | Google Secret Manager | Production secret storage |
| Containers | Google Artifact Registry | Release artifacts |
| Observability | Google Cloud Operations | Production telemetry |
| Mobile supporting services | Firebase where justified | Push, crash reporting, app protection and selected mobile services |
| Development/staging | Render | Fast multi-language integration environments |
| Database development/experimentation | Supabase/local PostgreSQL | Development provider, not canonical architecture |

## Why this is the recommendation

### 1. Google Cloud becomes the production home

Google Cloud is the strongest fit for Janavani's eventual production infrastructure because the ecosystem will require more than frontend hosting: durable PostgreSQL, object storage, background processing, eventing, secrets, observability and containerized services.

This does **not** mean Janavani becomes Google-specific. Every important dependency must sit behind a Janavani-owned provider-neutral contract.

### 2. Cloudflare is the edge layer

Cloudflare should be considered separately from application hosting. It can provide DNS, CDN, WAF/DDoS protection, edge routing and lightweight edge logic without owning Janavani's domain model.

Cloudflare Workers must not become the canonical domain runtime.

### 3. Vercel remains a WebApp delivery platform

Vercel is well suited to the WebApp/public-web delivery layer and preview workflow. The WebApp must consume typed Janavani capability contracts rather than embedding Case, Evidence, Authority, Consent or policy logic in frontend/serverless code.

### 4. Render remains valuable during development

Render is useful for fast Python/Rust services, Telegram Bot deployment, integration testing and staging. Its free tier should not be treated as the production home for sensitive citizen data or durable evidence.

### 5. Firebase is selective, not foundational

Firebase may support native mobile concerns such as push notifications, crash reporting and app protection. It should not become the canonical identity, case, evidence or domain backend merely because it is convenient for mobile.

### 6. Supabase is a provider, not the architecture

Supabase is useful for development and rapid PostgreSQL-backed experimentation. Janavani's repository contracts must continue to target PostgreSQL/provider-neutral interfaces so production can move to Cloud SQL or another compliant PostgreSQL provider without domain rewrites.

## Provider-neutrality rules

1. No provider-specific SDK may cross into the canonical domain kernel unless explicitly isolated behind an adapter.
2. PostgreSQL is treated as the persistence capability; Cloud SQL/Supabase/etc. are providers.
3. Object storage is treated as the artifact capability; GCS/S3-compatible storage/etc. are providers.
4. Messaging/eventing is treated as an infrastructure capability; Pub/Sub/etc. are providers.
5. Authentication is treated as an identity boundary; provider credentials/tokens are never citizen identity by themselves.
6. Vercel, Render, Cloudflare, Firebase and other surfaces/providers must not own canonical Case lifecycle or authorization decisions.
7. A provider outage must not silently corrupt or redefine domain state.
8. Free-tier limits must never determine canonical domain design.
9. Sensitive citizen evidence must not be placed in development/free-tier infrastructure merely for convenience.
10. Production provider selection is subject to security, privacy, data residency, reliability, cost, operational maturity and exit-strategy review.

## Current phase

Do not perform a production migration solely because the product is approaching readiness. First complete and verify the provider-neutral contracts, then perform a production-readiness assessment.

Render can continue as development/staging infrastructure. Vercel can continue for WebApp delivery. Supabase/local PostgreSQL can support development. Cloudflare can be introduced when edge/security routing provides concrete value.

## Production readiness gate

Before selecting final production infrastructure, verify:

```text
Canonical contracts
→ Identity/authentication
→ Authorization
→ Case lifecycle
→ Evidence/artifact lifecycle
→ Document generation
→ Consent/approval
→ Submission adapters
→ Audit/provenance
→ Security review
→ Privacy/data-flow review
→ Load/reliability tests
→ Disaster recovery
→ Observability
→ Cost model
→ Provider exit/migration test
→ Production provider selection
```

## Strategic conclusion

The final architecture should **not** be "Janavani on Google" or "Janavani on Vercel." It should be:

> **Janavani-owned capabilities deployed across provider infrastructure according to capability fit.**

The current preferred production composition is:

```text
                    JANAVANI
                       │
              Canonical Rust Core
                       │
              Shared Capabilities
                       │
       ┌───────────────┼────────────────┐
       │               │                │
   Cloudflare         Vercel          Clients
      Edge            WebApp       Telegram/Mobile/etc.
       │               │                │
       └───────────────┼────────────────┘
                       │
                 Google Cloud
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    Cloud Run       Cloud SQL        GCS
        │              │              │
      Jobs          PostgreSQL      Evidence
        │
     Pub/Sub
```

This is the **current recommendation**, not a permanent commitment. Reassess at the production-readiness gate using actual Janavani workload, security, privacy, reliability and cost evidence.
