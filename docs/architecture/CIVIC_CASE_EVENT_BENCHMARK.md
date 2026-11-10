# CivicCase Event-Chain Validation Benchmark

**Status:** Reproducible baseline harness; measurements not yet collected  
**Capability:** Pure in-memory `validate_event_chain` in Python and Rust  
**Purpose:** Determine whether this narrow deterministic workload benefits from Rust before considering a production migration.

## Commands

Run from the repository root, on the same machine and under similar system load:

```bash
python benchmarks/event_chain_validation.py 10000 30
cargo run --release -p janavani-core --example event_chain_bench -- 10000 30
```

Repeat each command at least five times. Record CPU, OS, Python version, rustc version, event count, repetition count, median and p95. Use a warm machine, avoid concurrent builds and compare release-mode Rust only.

## What this measures

- One in-memory event-chain validation pass.
- Same event count, IDs, case ID, event types and timestamps in both runtimes.
- Median and p95 elapsed time across repeated calls.
- Normalized median nanoseconds per event.

## What this does not measure

- Python↔Rust FFI or network-boundary overhead.
- PostgreSQL, serialization, HTTP, AI inference or end-to-end request latency.
- Production throughput under concurrent load.
- Memory allocation parity beyond what the runtimes naturally incur.
- Overall JANAVANI application performance.

The harness deliberately excludes fixture construction from the timed region. The Rust validator currently accepts owned events, so its benchmark clones the prebuilt event vector per iteration; the Python validator consumes an iterable without cloning. This asymmetry must be accounted for when interpreting results. A fair follow-up can compare both on prebuilt cloned inputs or redesign both APIs around borrowed/slice inputs, but do not change production APIs merely to improve benchmark scores.

## Acceptance criteria before migration

A Rust result is not sufficient by itself. Require:

1. Shared contract vectors pass in both languages.
2. Rust and Python produce identical accept/reject outcomes for valid and invalid chains.
3. The measured improvement is repeatable and material (recommended initial threshold: at least 2x median speedup on representative workloads).
4. The capability is actually on a measured application hot path.
5. Any FFI/service-boundary overhead is measured separately.
6. Memory, concurrency, error semantics, observability and rollback are assessed.
7. The Rust implementation becomes authoritative only after parity and operational acceptance.

If this validator is not a material bottleneck, retain the shared implementation contract and do not migrate this capability for performance alone.
