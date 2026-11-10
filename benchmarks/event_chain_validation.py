"""Comparable microbenchmark for the shared CivicCase event-chain validator.

Run from repository root:
    python benchmarks/event_chain_validation.py 10000 30
Compare with:
    cargo run --release -p janavani-core --example event_chain_bench -- 10000 30

This is a microbenchmark, not a production performance claim. Run both on the
same machine, under similar load, and repeat multiple times.
"""
from __future__ import annotations

import json
import statistics
import sys
import time

from src.core.case_events import CaseEvent
from src.core.case_helpers import validate_event_chain
from src.core.case_types import CaseEventType


def main() -> None:
    event_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    repetitions = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    if event_count < 1 or repetitions < 5:
        raise SystemExit("use at least one event and five repetitions")

    events = [
        CaseEvent(
            event_id=f"event-{index}",
            case_id="benchmark-case",
            event_type=CaseEventType.CREATED if index == 0 else CaseEventType.EVIDENCE_ADDED,
            occurred_at="2026-11-10T00:00:00Z",
        )
        for index in range(event_count)
    ]

    for _ in range(5):
        assert validate_event_chain(events)

    samples: list[int] = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        valid = validate_event_chain(events)
        elapsed = time.perf_counter_ns() - start
        assert valid, "benchmark validation unexpectedly failed"
        samples.append(elapsed)

    median = int(statistics.median(samples))
    p95 = sorted(samples)[round((len(samples) - 1) * 0.95)]
    print(
        json.dumps(
            {
                "runtime": "python",
                "event_count": event_count,
                "repetitions": repetitions,
                "median_ns": median,
                "p95_ns": p95,
                "median_ns_per_event": round(median / event_count, 3),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
