use janavani_core::{validate_event_chain, CaseEvent, CaseEventType};
use std::env;
use std::time::Instant;

fn percentile(sorted: &[u128], p: f64) -> u128 {
    let index = ((sorted.len() - 1) as f64 * p).round() as usize;
    sorted[index]
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let event_count: usize = args.get(1).and_then(|v| v.parse().ok()).unwrap_or(10_000);
    let repetitions: usize = args.get(2).and_then(|v| v.parse().ok()).unwrap_or(30);
    assert!(event_count >= 1 && repetitions >= 5, "use at least one event and five repetitions");

    let events: Vec<CaseEvent> = (0..event_count)
        .map(|index| {
            let event_type = if index == 0 { CaseEventType::Created } else { CaseEventType::EvidenceAdded };
            CaseEvent::new(
                format!("event-{index}"),
                "benchmark-case",
                event_type,
                "2026-11-10T00:00:00Z",
            )
        })
        .collect();

    for _ in 0..5 {
        assert!(validate_event_chain(&events));
    }

    let mut samples = Vec::with_capacity(repetitions);
    for _ in 0..repetitions {
        let start = Instant::now();
        let valid = validate_event_chain(&events);
        let elapsed = start.elapsed().as_nanos();
        assert!(valid, "benchmark validation unexpectedly failed");
        samples.push(elapsed);
    }
    samples.sort_unstable();
    let median = percentile(&samples, 0.50);
    let p95 = percentile(&samples, 0.95);

    println!(
        "{{\"runtime\":\"rust\",\"event_count\":{},\"repetitions\":{},\"median_ns\":{},\"p95_ns\":{},\"median_ns_per_event\":{:.3}}}",
        event_count,
        repetitions,
        median,
        p95,
        median as f64 / event_count as f64
    );
}
