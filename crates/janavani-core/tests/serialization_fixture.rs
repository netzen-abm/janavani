use janavani_core::CivicCase;
use serde_json::Value;
use std::fs;
use std::path::PathBuf;

fn fixture_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../tests/fixtures/civic_case_serialization.json")
}

#[test]
fn canonical_fixture_round_trips_through_rust_model() {
    let path = fixture_path();
    let source = fs::read_to_string(&path).expect("serialization fixture must exist");
    let expected: Value = serde_json::from_str(&source)
        .expect("serialization fixture must contain valid JSON");
    let case: CivicCase = serde_json::from_str(&source)
        .expect("canonical fixture must deserialize as CivicCase");
    let encoded = serde_json::to_value(&case)
        .expect("CivicCase must serialize as JSON");

    assert_eq!(encoded, expected);
}
