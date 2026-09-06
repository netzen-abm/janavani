#[path = "../src/consent.rs"]
mod consent;

use consent::{Consent, ConsentGrantType, ConsentStatus};

fn granted() -> Consent {
    Consent {
        consent_id: "consent-1".into(),
        subject_id: "subject-1".into(),
        purpose: "submit civic case".into(),
        scope: vec!["case_submission".into()],
        grant_type: ConsentGrantType::Explicit,
        status: ConsentStatus::Granted,
        created_at: "2026-09-06T00:00:00Z".into(),
        expires_at: None,
        revoked_at: None,
        proof_ref: None,
    }
}

#[test]
fn granted_consent_authorizes_exact_purpose_and_scope() {
    let consent = granted();
    assert!(consent.validate().is_ok());
    assert!(consent.is_authorized());
    assert!(consent.authorizes("submit civic case", "case_submission"));
    assert!(!consent.authorizes("other purpose", "case_submission"));
    assert!(!consent.authorizes("submit civic case", "other_scope"));
}

#[test]
fn revoked_consent_requires_revocation_timestamp() {
    let mut consent = granted();
    consent.status = ConsentStatus::Revoked;
    assert_eq!(
        consent.validate(),
        Err("revoked_at is required for revoked consent")
    );
}

#[test]
fn required_consent_cannot_have_empty_scope() {
    let mut consent = granted();
    consent.scope.clear();
    assert_eq!(
        consent.validate(),
        Err("scope must not be empty for required consent")
    );
}

#[test]
fn not_required_consent_can_have_empty_scope() {
    let mut consent = granted();
    consent.scope.clear();
    consent.grant_type = ConsentGrantType::NotRequired;
    assert!(consent.validate().is_ok());
}

#[test]
fn consent_serializes_with_canonical_values() {
    let consent = granted();
    let json = serde_json::to_value(consent).unwrap();
    assert_eq!(json["grant_type"], "explicit");
    assert_eq!(json["status"], "granted");
    assert_eq!(json["scope"][0], "case_submission");
}
