use janavani_core::CaseStatus;
use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../tests/fixtures/civic_case_transitions.json")
}

#[test]
fn rust_lifecycle_matches_canonical_transition_fixture() {
    let source = fs::read_to_string(fixture_path()).expect("transition fixture must exist");
    let expected: BTreeMap<String, Vec<String>> =
        serde_json::from_str(&source).expect("transition fixture must be valid JSON");

    let statuses = [
        CaseStatus::Draft,
        CaseStatus::Review,
        CaseStatus::Ready,
        CaseStatus::Submitting,
        CaseStatus::Queued,
        CaseStatus::Submitted,
        CaseStatus::Acknowledged,
        CaseStatus::FollowUp,
        CaseStatus::InProgress,
        CaseStatus::Responded,
        CaseStatus::Resolved,
        CaseStatus::Escalated,
        CaseStatus::Closed,
        CaseStatus::Archived,
    ];

    let mut actual = BTreeMap::new();
    for status in statuses {
        let key = serde_json::to_value(status).unwrap().as_str().unwrap().to_owned();
        let mut targets = Vec::new();
        for target in statuses {
            if status.can_transition(target) {
                targets.push(serde_json::to_value(target).unwrap().as_str().unwrap().to_owned());
            }
        }
        targets.sort();
        actual.insert(key, targets);
    }

    assert_eq!(actual, expected);
}
