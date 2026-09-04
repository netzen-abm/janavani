use janavani_core::{CaseEventType, CaseType, CivicCase, DomainError};

fn ready_case() -> CivicCase {
    let mut case = CivicCase::new(
        "case-parity",
        CaseType::Complaint,
        "Delayed service",
        "The requested service remains pending.",
    );
    case.consent_refs.push("consent-1".into());
    case.start_review("event-1", "2026-09-04T00:00:00Z", None).unwrap();
    case.mark_ready("event-2", "2026-09-04T00:01:00Z", None).unwrap();
    case.begin_submission("event-3", "2026-09-04T00:02:00Z", None, None).unwrap();
    case.submit("event-4", "2026-09-04T00:03:00Z", None, None).unwrap();
    case
}

#[test]
fn acknowledgement_event_notes_are_persisted() {
    let mut case = ready_case();
    let returned = case
        .acknowledge(
            "event-5",
            "2026-09-04T00:04:00Z",
            None,
            Some("web".into()),
            Some("ACK-1".into()),
            Some("Received by authority".into()),
        )
        .unwrap();

    assert_eq!(returned.event_type, CaseEventType::Acknowledged);
    assert_eq!(returned.notes.as_deref(), Some("Received by authority"));
    assert_eq!(case.events.last().unwrap(), &returned);
}

#[test]
fn notes_are_not_encoded_as_source_reference() {
    let mut case = ready_case();
    case.acknowledge(
        "event-5",
        "2026-09-04T00:04:00Z",
        None,
        Some("web".into()),
        Some("ACK-1".into()),
        None,
    )
    .unwrap();

    let result = case.follow_up(
        "event-6",
        "2026-09-04T00:05:00Z",
        None,
        Some("First follow-up".into()),
    );
    assert!(result.is_ok());
    let event = case.events.last().unwrap();
    assert_eq!(event.notes.as_deref(), Some("First follow-up"));
    assert_eq!(event.source_ref, None);
}

#[test]
fn duplicate_event_rejection_does_not_change_case_status() {
    let mut case = ready_case();
    let before = case.clone();
    let result = case.begin_submission("event-3", "2026-09-04T00:06:00Z", None, None);
    assert_eq!(result, Err(DomainError::DuplicateEventId));
    assert_eq!(case, before);
}
