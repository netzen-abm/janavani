# Rust–Python Interoperability and AI Runtime Boundary

**Status:** Proposed implementation policy aligned with the adopted Rust Core Strategy  
**Decision date:** 2026-11-10  
**Scope:** Janavani application runtime, AI/RAG services, domain kernel, and future native bindings

## 1. Executive decision

Janavani should use a **Rust domain/runtime core with Python application and AI orchestration at the edges**, migrated incrementally. This is a polyglot architecture, not a wholesale language rewrite.

The repository already records the strategic direction in `RUST_CORE_STRATEGY.md`: Rust is the target for canonical shared domain behavior, while Python remains valid for adapters, AI/RAG experimentation, legacy migration and channel integrations. This document makes the Python/Rust boundary, concurrency policy and performance gates explicit.

**Do not migrate code to Rust merely because the wider AI industry is adopting Rust.** Migrate when a measured reliability, security, latency, throughput, memory or operational requirement justifies the cost.

## 2. What the industry trend does—and does not—mean

Rust provides compile-time ownership and borrowing checks that prevent broad classes of memory-safety errors in safe Rust. It also provides strong primitives for data-race-resistant concurrency. Unsafe Rust, FFI boundaries, logic defects, resource exhaustion and distributed-system failures still require review and runtime controls.

C++ remains deeply embedded in mature AI/GPU libraries, drivers and vendor ecosystems. Rust does not automatically replace CUDA, ROCm, vendor kernels or mature C++ inference/training runtimes. A Rust wrapper does not make the underlying accelerator stack Rust-native.

Python remains a productive high-level language for model development, data science, AI provider SDKs, RAG orchestration and application integration. The practical target is to keep Python where its ecosystem and iteration speed are valuable, and move deterministic shared domain logic or measured hot paths to Rust.

## 3. Target Janavani architecture

```text
Independent product surfaces
  Web | Telegram | WhatsApp | Android | iOS | future clients
                         |
              Authenticated API / adapters
                         |
             Python application orchestration
       AI / RAG / model providers / workflow composition
                         |
              Versioned domain contract boundary
                         |
                Rust canonical domain core
       Case | lifecycle | events | consent | invariants
                         |
               Ports / provider interfaces
                         |
        PostgreSQL | object storage | external systems
```

This is the **target direction**, not a claim that every domain capability has already migrated. Existing Python production behavior remains authoritative until the equivalent Rust implementation, contract tests, migration evidence and deployment path are accepted.

### Rust should own, as it is safely migrated

- deterministic domain entities and invariants;
- CivicCase lifecycle transition rules;
- canonical event types and serialization;
- consent and authorization decision primitives;
- evidence metadata/provenance validation;
- deterministic policy evaluation;
- CPU-bound parsing, validation or transformation hot paths when benchmarks justify migration;
- high-concurrency infrastructure components where isolation and throughput benefits are demonstrated.

### Python should continue to own where it is the better fit

- AI/LLM provider integration and model orchestration;
- RAG pipelines, retrieval experimentation and evaluation;
- prompt and tool orchestration;
- rapidly changing application workflows;
- data-science/model experimentation;
- web/API and channel adapters until a separately justified migration;
- integration glue and operational scripts.

A Python adapter may call the Rust kernel, but it must not fork the domain rules or independently reinterpret lifecycle, consent, authority or submission semantics.

## 4. Interoperability decision: contracts first, bindings later

Use a versioned, language-neutral contract as the source of interoperability truth:

- stable event and enum values (canonical `snake_case` on the wire);
- explicit request/response schemas;
- stable error codes and validation semantics;
- versioned compatibility rules;
- golden serialization fixtures;
- cross-language conformance tests;
- deterministic handling of unknown fields and unknown enum values.

Prefer a process boundary (HTTP or gRPC with a versioned schema) when Rust and Python components need independent deployment, scaling, failure isolation or release cadence.

Consider **PyO3** only when all of the following are true:

1. profiling identifies Python↔Rust call overhead or data-copy cost as a material bottleneck;
2. an in-process native extension is operationally preferable to a service boundary;
3. the exposed API can be coarse-grained (batch operations rather than per-record chatty calls);
4. ownership, lifetime, panic/error translation and shutdown behavior are specified;
5. wheels/builds are supported for every target OS, architecture and Python ABI;
6. standard and free-threaded Python compatibility are tested where claimed;
7. the extension has a documented fallback or safe failure mode.

Do not add PyO3 as a dependency until a concrete use case and benchmark justify it. The currently inspected root `Cargo.toml` and `pyproject.toml` do not declare a PyO3/maturin bridge.

## 5. GIL and concurrency policy

Do not state that Rust automatically removes the Python GIL. Rust-native work can execute concurrently outside Python, but calls into the Python runtime still obey the interpreter's attachment and GIL/free-threading rules.

CPython introduced an experimental free-threaded build in 3.13 and supports the free-threaded build in 3.14. This is an optional build/runtime path, not a safe assumption for every Python dependency. An extension that is not marked and audited for free-threading may cause the GIL to be enabled again.

PyO3 supports free-threaded CPython, but the extension author must ensure its Rust and exposed Python objects are genuinely thread-safe. Do not infer thread safety solely from using Rust or from compiling successfully.

For Janavani:

- keep production on the project's currently supported standard Python build unless a separate compatibility programme approves otherwise;
- treat free-threaded CPython as an opt-in evaluation track;
- audit every native extension and dependency before enabling it;
- run concurrency, race, shutdown and load tests on the actual deployment build;
- never use the GIL as the only protection for domain or database invariants.

## 6. GPU and AI execution policy

Do not write a custom Rust GPU execution layer as a default response to this trend.

Keep model training/inference on mature, supported AI frameworks and hardware runtimes unless a specific workload demonstrates a compelling reason to change. Rust can manage request routing, batching, queues, policy checks, preprocessing and service orchestration around those runtimes.

Any Rust GPU experiment must specify:
- exact workload and model;
- target hardware and driver/runtime;
- baseline framework and version;
- throughput, latency (including p95/p99), memory and cost;
- numerical correctness/tolerance;
- deployment and observability impact;
- maintenance and portability costs.

A faster microbenchmark is not sufficient if end-to-end model serving, GPU utilisation or operating cost does not improve.

## 7. Performance and migration gates

Every proposed Python-to-Rust migration must provide a before/after benchmark and an explicit reason. At minimum measure:

| Dimension | Required evidence |
|---|---|
| Correctness | Shared contract and golden-fixture parity |
| Latency | p50, p95 and p99 under representative load |
| Throughput | Sustained requests/operations per second |
| CPU | Core utilisation and saturation behavior |
| Memory | RSS/peak allocation and leak checks |
| Concurrency | Race, contention, cancellation and shutdown tests |
| Reliability | Failure injection, retries and restart behavior |
| Security | Unsafe/FFI review, dependency and supply-chain checks |
| Operations | Build, deployment, rollback and observability cost |

Migration sequence:

1. Freeze the domain contract and current Python behavior with tests.
2. Implement the equivalent Rust behavior in the canonical crate.
3. Run cross-language contract and serialization tests.
4. Benchmark realistic end-to-end workloads.
5. Introduce one Rust-backed capability behind an adapter boundary.
6. Shadow or canary it where safe; compare outcomes.
7. Switch authority only after parity, rollback and operational acceptance.
8. Retire the Python implementation only after references, production dependencies and recovery paths are verified.

Never run two competing authoritative implementations of consent, case lifecycle or consequential-action policy.

## 8. Mojo and other emerging languages

Mojo and other emerging systems languages may be tracked as research options. They are not an approved production runtime for Janavani at this time. Adoption requires ecosystem maturity, supported toolchains, security review, interoperability evidence, hiring/maintenance capacity and a demonstrated advantage over the current Rust/Python split.

## 9. Current repository observations

At the reviewed branch snapshot:

- `Cargo.toml` defines the Rust workspace with `janavani-core` and `janavani-application`.
- `crates/janavani-core` is a small domain crate using Serde/Serde JSON.
- `crates/janavani-application` depends on the core crate.
- `pyproject.toml` defines the Python application and AI/data ecosystem dependencies.
- No PyO3 or maturin bridge is declared in the inspected manifests.
- The existing Rust strategy already says not to rewrite the working Python system wholesale.

These observations support an incremental polyglot approach. They do not establish that the Rust kernel is already the production authority for every listed domain.

## 10. Decision summary

**Adopt:** Rust for the canonical domain kernel as capabilities are proven and migrated; Python for AI/RAG and application orchestration where it remains the better fit; versioned contracts between them.

**Defer:** PyO3, free-threaded CPython in production, Rust GPU execution, Mojo, and wholesale application rewrites until workload-specific evidence justifies them.

**Non-negotiable:** One domain meaning, one authoritative decision path, versioned cross-language contracts, measurable migration benefits, and a tested rollback path.

## 11. Technical references

- CPython free-threading HOWTO: https://docs.python.org/3/howto/free-threading-python.html
- CPython 3.13 free-threaded mode background: https://docs.python.org/3/whatsnew/3.13.html
- PyO3 free-threading guide: https://pyo3.rs/main/free-threading
- PyO3 Python/Rust interoperability guide: https://pyo3.rs/main/
- Rust ownership and borrowing: https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
- Rust concurrency: https://doc.rust-lang.org/book/ch16-00-concurrency.html
