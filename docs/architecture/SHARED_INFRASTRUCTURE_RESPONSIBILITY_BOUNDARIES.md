# JANAVANI — Shared Infrastructure Responsibility Boundaries

**Status:** CANONICAL ARCHITECTURE CONTRACT  
**Purpose:** Define where Janavani separates code and where it deliberately preserves cohesion.

## 1. Architectural rule

Janavani is one shareable infrastructure with independently operable access surfaces.

Code is split only when the split creates a real boundary of:

- **change** — the responsibility can evolve independently;
- **trust** — authorization, consent, identity, or privacy requires a distinct enforcement boundary;
- **persistence** — durable storage has different consistency/transaction semantics;
- **provider dependency** — an external implementation can be replaced without changing domain semantics;
- **independent reuse** — multiple surfaces or capabilities consume the same contract.

Code must remain cohesive when splitting it would:

- duplicate orchestration;
- weaken an invariant;
- create competing sources of truth;
- force a surface to reconstruct domain state;
- create circular dependencies;
- or add abstraction without an independently testable architectural boundary.

**Class/file size is not a splitting criterion.**

## 2. Canonical dependency direction

```text
Access Surface / Adapter
        |
        v
Capability Contract + Execution Context
        |
        v
Trust / Authorization / Consent
        |
        v
Domain Aggregate + Lifecycle Invariants
        |
        +--> Content / Evidence references
        |
        v
Submission / Delivery Contract
        |
        v
Unit of Work / Transaction Boundary
        |
        v
Provider Adapter
        |
        v
PostgreSQL / external provider
```

Surfaces may depend on capabilities. Capabilities must not depend on Web, Telegram, WhatsApp, mobile UI, or another surface.

Providers implement persistence/delivery contracts. Providers must not become the domain model.

## 3. Boundaries that are intentionally separate

### 3.1 Surface adapters

**Examples**

- `src/web/`
- Telegram bootstrap and command/conversation adapters
- future Android, iOS, WhatsApp, Messenger, DApp adapters

**Own**

- transport/protocol concerns;
- request/response or message formatting;
- surface-specific identity acquisition;
- mapping external input to capability requests.

**Must not own**

- CivicCase lifecycle rules;
- authorization policy duplicated from the canonical capability;
- persistence transactions;
- provider-specific business semantics.

A surface failure must not disable another surface.

### 3.2 Capability layer

**Examples**

- `src/capabilities/civic_case.py`
- Civic Action, Evidence, Consent, Authority, Document and Submission capabilities

**Own**

- reusable commands/queries;
- capability-level authorization invocation;
- canonical orchestration of the capability's domain operation;
- execution-context validation.

This is the principal reuse boundary across surfaces.

### 3.3 Domain kernel

**Examples**

- `src/core/civic_case.py`
- `src/core/case_lifecycle.py`
- Rust `janavani-core`

**Own**

- domain state;
- lifecycle invariants;
- canonical state/event semantics;
- cross-language parity contracts.

The domain kernel must not import surface, provider, or transport implementations.

Keep aggregate state and invariant logic together when separating them would make it possible to mutate state without enforcing the invariant.

### 3.4 Sensitive content boundary

Citizen-authored narrative/claims and durable lifecycle metadata have different privacy and persistence characteristics.

Where the contract requires transient or separately protected content, content handling remains behind the Case content boundary rather than being duplicated in each surface.

This boundary is justified by **trust + persistence + privacy**, not by code size.

### 3.5 Persistence / Unit of Work

**Examples**

- `src/storage/repositories/`
- `src/storage/postgres_unit_of_work.py`

**Own**

- provider-neutral repository contracts;
- PostgreSQL implementation;
- transaction atomicity;
- persistence-level authorization/RLS behavior.

The Unit of Work remains cohesive with transaction lifecycle handling. Splitting `__enter__`/`__exit__`, commit/rollback semantics into unrelated orchestration layers would weaken the atomicity invariant.

### 3.6 External delivery providers

Submission transport is separate from Case lifecycle and persistence because delivery is an external side effect with independent failure and acknowledgement semantics.

A provider failure must not corrupt the Case aggregate or silently change lifecycle state.

## 4. Shared composition

`src/platform/` is the composition boundary that assembles one provider graph and one capability graph for a surface.

The same composition principles apply to Web and Telegram:

```text
                 Shared Platform Composition
                          |
          +---------------+---------------+
          |                               |
       Web adapter                    Telegram adapter
          |                               |
          +---------------+---------------+
                          |
                 Shared capabilities
                          |
                 Shared domain/storage
```

A surface may have its own adapter-specific composition only when required by its runtime lifecycle. It must not construct a second implementation of the same domain capability merely because it is a different surface.

## 5. Current canonical responsibility map

| Responsibility | Canonical boundary | Why separate? |
|---|---|---|
| HTTP | `src/web/` | protocol/change boundary |
| Telegram runtime | `src/bot_telegram.py` + adapters | independent runtime/transport boundary |
| Case capability | `src/capabilities/` | reusable business capability |
| Case lifecycle | `src/core/` | invariant boundary |
| Case content | content repository/capability boundary | privacy + persistence boundary |
| Evidence | Evidence capability/repository | independent reusable capability |
| Consent | Consent capability/repository | trust boundary |
| Authority | Authority capability/repository | reusable policy/data boundary |
| Documents | document capability/artifact providers | provider/output boundary |
| Submission | submission contract/provider | external side-effect boundary |
| PostgreSQL | storage provider | persistence/provider boundary |
| Agent platform | agent gateway/contracts | execution/trust boundary |
| Rust parity | `crates/janavani-core` + parity tests | language/runtime boundary |

## 6. Anti-patterns explicitly prohibited

1. Surface directly mutating `CivicCase` lifecycle state.
2. A second Case capability implementation for Telegram/Web/mobile.
3. Provider SDK imports in the domain kernel.
4. Surface-specific authorization that bypasses canonical policy.
5. Persistence code embedded in HTTP/message handlers.
6. External delivery acknowledgement being treated as database persistence success.
7. Splitting tightly coupled invariant logic merely to reduce file size.
8. Creating an abstraction layer without an independent change, trust, persistence, provider, or reuse boundary.
9. Reintroducing archived generations into the active runtime graph.

## 7. Branch hygiene

The repository is maintained at exactly **nine active branches**.

Branch count is a governance constraint, not an excuse to preserve obsolete architecture generations. A branch may remain only when it represents one of the current integration, audit, feature, or architecture workstreams.

Before any branch is removed:

1. inspect its commits and open PRs;
2. determine whether unique work is already represented in `main`;
3. preserve required historical evidence in archive/docs;
4. merge only when the target is green and architecturally coherent;
5. otherwise close/delete safely without losing the evidence.

Do not create a tenth active branch for routine work.

## 8. Definition of architectural success

The architecture is successful when:

- Web can fail without taking Telegram down;
- Telegram can fail without taking Web down;
- both use the same canonical capability semantics;
- lifecycle invariants have one authoritative implementation per language;
- PostgreSQL is replaceable behind repository/provider contracts;
- sensitive content is not duplicated into unrelated persistence paths;
- external delivery is isolated from durable state;
- security policy is enforced at canonical trust boundaries;
- new surfaces can be added mostly as adapters rather than new business-logic stacks.

This contract is intentionally conservative: **split at real boundaries; preserve cohesion everywhere else.**
