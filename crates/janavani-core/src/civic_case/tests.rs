#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn make_case() -> CivicCase {
        let mut case = CivicCase::new("case-1", CaseType::Complaint, "Delayed public service", "The requested service has not been delivered.");
        case.consent_refs.push("consent-1".into());
        case.start_review("event-1", "2026-08-24T00:00:00Z", None).unwrap();
        case.mark_ready("event-2", "2026-08-24T00:01:00Z", None).unwrap();
        case
    }

    #[test]
    fn aggregate_preserves_canonical_fields_and_lifecycle() {
        let mut case = make_case();
        case.jurisdiction.insert("district".into(), json!("Bengaluru Urban"));
        case.related_official_id = Some("official-1".into());
        case.begin_submission("event-3", "2026-08-24T00:02:00Z", None, None).unwrap();
        case.submit("event-4", "2026-08-24T00:03:00Z", None, None).unwrap();
        case.acknowledge("event-5", "2026-08-24T00:04:00Z", None, Some("web".into()), Some("ACK-1".into()), None).unwrap();
        assert_eq!(case.status, CaseStatus::Acknowledged);
        assert!(case.confirmed_delivery());
        assert_eq!(case.events.len(), 5);
    }

    #[test]
    fn json_domain_values_round_trip_without_narrowing() {
        let mut case = make_case();
        case.jurisdiction.insert("district".into(), json!({"name": "Pune", "rank": 3, "active": true}));
        case.jurisdiction.insert("levels".into(), json!(["state", "district"]));
        case.claims.push(BTreeMap::from([("claim".into(), json!("road damage")), ("verified".into(), json!(false)), ("confidence".into(), json!(0.75)), ("tags".into(), json!(["road", "public-service"])), ("metadata".into(), json!({"source": null}))]));
        let encoded = serde_json::to_string(&case).unwrap();
        let decoded: CivicCase = serde_json::from_str(&encoded).unwrap();
        assert_eq!(decoded, case);
    }

    #[test]
    fn acknowledgement_event_notes_are_persisted() {
        let mut case = make_case();
        case.begin_submission("event-3", "2026-08-24T00:02:00Z", None, None).unwrap();
        case.submit("event-4", "2026-08-24T00:03:00Z", None, None).unwrap();
        let event = case.acknowledge("event-5", "2026-08-24T00:04:00Z", None, Some("web".into()), Some("ACK-1".into()), Some("Received by office".into())).unwrap();
        assert_eq!(event.notes.as_deref(), Some("Received by office"));
        assert_eq!(case.events.last().unwrap().notes.as_deref(), Some("Received by office"));
        assert_eq!(case.events.last().unwrap().source_ref.as_deref(), Some("ACK-1"));
    }

    #[test]
    fn notes_are_not_encoded_as_source_reference() {
        let mut case = make_case();
        case.begin_submission("event-3", "2026-08-24T00:02:00Z", None, None).unwrap();
        case.submit("event-4", "2026-08-24T00:03:00Z", None, None).unwrap();
        case.acknowledge("event-5", "2026-08-24T00:04:00Z", None, Some("web".into()), Some("ACK-1".into()), Some("Received by office".into())).unwrap();
        case.follow_up("event-6", "2026-08-24T00:05:00Z", None, Some("Request status update".into())).unwrap();
        let event = case.events.last().unwrap();
        assert_eq!(event.notes.as_deref(), Some("Request status update"));
        assert_eq!(event.source_ref, None);
    }

    #[test]
    fn duplicate_event_does_not_mutate_status() {
        let mut case = make_case();
        let before_status = case.status;
        let before_events = case.events.clone();
        let result = case.begin_submission("event-1", "2026-08-24T00:02:00Z", None, None);
        assert_eq!(result, Err(DomainError::DuplicateEventId));
        assert_eq!(case.status, before_status);
        assert_eq!(case.events, before_events);
    }

    #[test]
    fn duplicate_event_does_not_mutate_evidence() {
        let mut case = make_case();
        let before = case.evidence_refs.clone();
        let result = case.add_evidence("evidence-1", "event-1", "2026-08-24T00:02:00Z", None, None);
        assert_eq!(result, Err(DomainError::DuplicateEventId));
        assert_eq!(case.evidence_refs, before);
    }

    #[test]
    fn duplicate_event_does_not_mutate_document_refs() {
        let mut case = make_case();
        let before = case.document_refs.clone();
        let result = case.add_document("document-1", "event-1", "2026-08-24T00:02:00Z", None, None);
        assert_eq!(result, Err(DomainError::DuplicateEventId));
        assert_eq!(case.document_refs, before);
    }

    #[test]
    fn duplicate_event_does_not_mutate_editable_content() {
        let mut case = make_case();
        let before_subject = case.subject.clone();
        let before_narrative = case.narrative.clone();
        let result = case.edit("event-1", "2026-08-24T00:02:00Z", None, Some("Changed subject".into()), Some("Changed narrative".into()));
        assert_eq!(result, Err(DomainError::DuplicateEventId));
        assert_eq!(case.subject, before_subject);
        assert_eq!(case.narrative, before_narrative);
    }

    #[test]
    fn consent_gate_is_enforced() {
        let mut case = CivicCase::new("case-1", CaseType::Complaint, "Subject", "Narrative");
        case.start_review("event-1", "2026-08-24T00:00:00Z", None).unwrap();
        assert_eq!(case.mark_ready("event-2", "2026-08-24T00:01:00Z", None), Err(DomainError::ConsentRequired));
    }

    #[test]
    fn duplicate_and_cross_case_events_are_rejected() {
        let mut case = make_case();
        assert!(matches!(case.begin_submission("event-1", "2026-08-24T00:02:00Z", None, None), Err(DomainError::DuplicateEventId)));
        let mut event = CaseEvent::new("event-9", "case-2", CaseEventType::Edited, "2026-08-24T00:05:00Z");
        event.notes = Some("wrong case".into());
        assert_eq!(case.record(event), Err(DomainError::EventBelongsToDifferentCase));
    }

    #[test]
    fn event_chain_keeps_orthogonal_events_outside_status_graph() {
        let events = vec![
            CaseEvent::new("1", "case-1", CaseEventType::Created, "2026-08-24T00:00:00Z"),
            CaseEvent::new("2", "case-1", CaseEventType::EvidenceAdded, "2026-08-24T00:01:00Z"),
            CaseEvent::new("3", "case-1", CaseEventType::Edited, "2026-08-24T00:02:00Z"),
        ];
        assert!(validate_event_chain(events));
    }

    #[test]
    fn canonical_lifecycle_and_delivery_boundary_remain_intact() {
        use super::CaseStatus::*;
        assert!(Draft.can_transition(Review));
        assert!(Acknowledged.can_transition(InProgress));
        assert!(Closed.can_transition(Archived));
        assert!(!Submitted.confirmed_delivery());
        assert!(Acknowledged.confirmed_delivery());
        assert!(!Archived.confirmed_delivery());
    }

    #[test]
    fn citizen_outcome_events_are_distinct_from_correction() {
        assert_ne!(CaseEventType::CitizenVerified, CaseEventType::Correction);
        assert_ne!(CaseEventType::CitizenReopened, CaseEventType::Correction);
        assert_eq!(serde_json::to_string(&CaseEventType::CitizenVerified).unwrap(), "\"citizen_verified\"");
        assert_eq!(serde_json::to_string(&CaseEventType::CitizenReopened).unwrap(), "\"citizen_reopened\"");
    }

    #[test]
    fn citizen_verification_and_reopen_have_explicit_events() {
        let mut case = make_case();
        case.begin_submission("event-3", "2026-08-24T00:02:00Z", None, None).unwrap();
        case.submit("event-4", "2026-08-24T00:03:00Z", None, None).unwrap();
        case.acknowledge("event-5", "2026-08-24T00:04:00Z", None, Some("web".into()), Some("ACK-1".into()), None).unwrap();
        case.respond("event-6", "2026-08-24T00:05:00Z", None, None).unwrap();
        case.resolve("event-7", "2026-08-24T00:06:00Z", None, None).unwrap();
        case.verify_resolution("event-8", "2026-08-24T00:07:00Z", Some("citizen:1".into()), Some("web".into()), Some("observation-1".into()), None).unwrap();
        assert_eq!(case.status, CaseStatus::Resolved);
        assert!(case.citizen_verified_resolution());
        assert_eq!(case.events.last().unwrap().event_type, CaseEventType::CitizenVerified);
        case.reopen_after_citizen_verification("event-9", "2026-08-24T00:08:00Z", Some("citizen:1".into()), Some("web".into()), Some("Issue remains".into())).unwrap();
        assert_eq!(case.status, CaseStatus::FollowUp);
        assert_eq!(case.events.last().unwrap().event_type, CaseEventType::CitizenReopened);
    }

    #[test]
    fn serde_uses_contract_values() {
        assert_eq!(serde_json::to_string(&CaseType::TransferConcern).unwrap(), "\"transfer_concern\"");
        assert_eq!(serde_json::to_string(&CaseStatus::FollowUp).unwrap(), "\"follow_up\"");
        assert_eq!(serde_json::to_string(&CaseEventType::ReviewStarted).unwrap(), "\"review_started\"");
    }
}
