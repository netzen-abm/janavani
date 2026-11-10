use super::{validate_event_chain, CaseEvent};

#[test]
fn event_chain_matches_shared_python_rust_contract_vectors() {
    let vectors: serde_json::Value = serde_json::from_str(include_str!(
        "../../../../tests/fixtures/civic_case_event_contract_v1.json"
    ))
    .unwrap();

    let parse_events = |key: &str| -> Vec<CaseEvent> {
        serde_json::from_value(vectors[key].clone()).unwrap()
    };

    assert_eq!(vectors["contract_version"], "1.0");
    assert!(validate_event_chain(&parse_events("valid_chain")));
    assert!(!validate_event_chain(&parse_events("invalid_ack_then_submitted")));
    assert!(!validate_event_chain(&parse_events("invalid_duplicate_ids")));
    assert!(!validate_event_chain(&parse_events("invalid_mixed_cases")));
}
