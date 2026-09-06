#[path = "../src/consent.rs"]
mod consent;

use consent::Consent;
use serde_json::Value;
use std::fs;

#[test]
fn rust_consent_round_trips_canonical_fixture() {
    let path = "../../tests/fixtures/consent_serialization.json";
    let text = fs::read_to_string(path).expect("consent fixture must exist");
    let expected: Value = serde_json::from_str(&text)
        .expect("fixture must be valid JSON");
    let consent: Consent = serde_json::from_value(expected.clone())
        .expect("fixture must deserialize as canonical Consent");
    assert!(consent.validate().is_ok());
    let encoded = serde_json::to_value(consent).expect("Consent must serialize");
    assert_eq!(encoded, expected);
}
