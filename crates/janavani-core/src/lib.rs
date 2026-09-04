//! Canonical, channel-neutral Janavani domain kernel.
//!
//! This crate contains the CivicCase aggregate, event model, and lifecycle
//! contract. It intentionally contains no database, Telegram, HTTP, AI, or UI
//! dependencies.

use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CaseType {
    Complaint,
    Grievance,
    Rti,
    Petition,
    Representation,
    Objection,
    Appeal,
    Corruption,
    Misbehaviour,
    TransferConcern,
    Other,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CaseStatus {
    Draft,
    Review,
    Ready,
    Submitting,
    Queued,
    Submitted,
    Acknowledged,
    FollowUp,
    InProgress,
    Responded,
    Resolved,
    Escalated,
    Closed,
    Archived,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CaseEventType {
    Created,
    Edited,
    ReviewStarted,
    Approved,
    EvidenceAdded,
    DocumentAdded,
    Submitting,
    Queued,
    Submitted,
    Acknowledged,
    FollowUp,
    Response,
    Resolved,
    Escalated,
    Correction,
    Closed,
    Archived,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CaseEvent {
    pub event_id: String,
    pub case_id: String,
    pub event_type: CaseEventType,
    pub occurred_at: String,
    pub actor_id: Option<String>,
    pub source_channel: Option<String>,
    pub source_ref: Option<String>,
    pub notes: Option<String>,
}

impl CaseEvent {
    pub fn new(
        event_id: impl Into<String>,
        case_id: impl Into<String>,
        event_type: CaseEventType,
        occurred_at: impl Into<String>,
    ) -> Self {
        Self {
            event_id: event_id.into(),
            case_id: case_id.into(),
            event_type,
            occurred_at: occurred_at.into(),
            actor_id: None,
            source_channel: None,
            source_ref: None,
            notes: None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CivicCase {
    pub case_id: String,
    pub case_type: CaseType,
    pub subject: String,
    pub narrative: String,
    pub created_by: Option<String>,
    pub jurisdiction: BTreeMap<String, String>,
    pub related_organisation_id: Option<String>,
    pub related_office_id: Option<String>,
    pub related_official_id: Option<String>,
    pub related_representative_id: Option<String>,
    pub claims: Vec<BTreeMap<String, String>>,
    pub evidence_refs: Vec<String>,
    pub document_refs: Vec<String>,
    pub consent_refs: Vec<String>,
    pub status: CaseStatus,
    pub events: Vec<CaseEvent>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
    pub version: u64,
}

impl CivicCase {
    pub fn new(
        case_id: impl Into<String>,
        case_type: CaseType,
        subject: impl Into<String>,
        narrative: impl Into<String>,
    ) -> Self {
        Self {
            case_id: case_id.into(),
            case_type,
            subject: subject.into(),
            narrative: narrative.into(),
            created_by: None,
            jurisdiction: BTreeMap::new(),
            related_organisation_id: None,
            related_office_id: None,
            related_official_id: None,
            related_representative_id: None,
            claims: Vec::new(),
            evidence_refs: Vec::new(),
            document_refs: Vec::new(),
            consent_refs: Vec::new(),
            status: CaseStatus::Draft,
            events: Vec::new(),
            created_at: None,
            updated_at: None,
            version: 1,
        }
    }

    pub fn edit(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        subject: Option<String>,
        narrative: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.ensure_editable()?;
        if let Some(value) = subject {
            self.subject = value.trim().to_owned();
        }
        if let Some(value) = narrative {
            self.narrative = value.trim().to_owned();
        }
        let mut event = CaseEvent::new(
            event_id,
            self.case_id.clone(),
            CaseEventType::Edited,
            occurred_at,
        );
        event.actor_id = actor_id;
        self.record(event)
    }

    pub fn start_review(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if self.status != CaseStatus::Draft {
            return Err(DomainError::InvalidOperation("Only a draft case can enter review"));
        }
        self.ensure_content()?;
        self.status = CaseStatus::Review;
        self.status_event(event_id, occurred_at, CaseEventType::ReviewStarted, actor_id, None, None)
    }

    pub fn mark_ready(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Review | CaseStatus::Ready) {
            return Err(DomainError::InvalidOperation("Cannot approve this case status"));
        }
        self.ensure_content()?;
        if self.consent_refs.is_empty() {
            return Err(DomainError::ConsentRequired);
        }
        self.status = CaseStatus::Ready;
        self.status_event(event_id, occurred_at, CaseEventType::Approved, actor_id, None, None)
    }

    pub fn begin_submission(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Ready, "Only a ready case can begin submission")?;
        self.status = CaseStatus::Submitting;
        self.status_event(event_id, occurred_at, CaseEventType::Submitting, actor_id, source_channel, None)
    }

    pub fn queue_submission(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Submitting, "Only a submitting case can be queued")?;
        self.status = CaseStatus::Queued;
        self.status_event(event_id, occurred_at, CaseEventType::Queued, actor_id, source_channel, None)
    }

    pub fn submit(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Submitting | CaseStatus::Queued) {
            return Err(DomainError::InvalidOperation("Only a submitting or queued case can be submitted"));
        }
        self.status = CaseStatus::Submitted;
        self.status_event(event_id, occurred_at, CaseEventType::Submitted, actor_id, source_channel, None)
    }

    pub fn acknowledge(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
        source_ref: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Submitted, "Only a submitted case can be acknowledged")?;
        self.status = CaseStatus::Acknowledged;
        self.status_event(
            event_id,
            occurred_at,
            CaseEventType::Acknowledged,
            actor_id,
            source_channel,
            source_ref,
        )
        .map(|mut event| {
            event.notes = notes;
            event
        })
    }

    pub fn follow_up(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Acknowledged | CaseStatus::InProgress | CaseStatus::Responded) {
            return Err(DomainError::InvalidOperation("Case is not ready for follow-up"));
        }
        self.status = CaseStatus::FollowUp;
        self.status_event(event_id, occurred_at, CaseEventType::FollowUp, actor_id, None, notes)
    }

    pub fn respond(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Acknowledged | CaseStatus::FollowUp | CaseStatus::InProgress | CaseStatus::Escalated) {
            return Err(DomainError::InvalidOperation("Case is not ready for a response"));
        }
        self.status = CaseStatus::Responded;
        self.status_event(event_id, occurred_at, CaseEventType::Response, actor_id, None, notes)
    }

    pub fn resolve(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Responded, "Only a responded case can be resolved")?;
        self.status = CaseStatus::Resolved;
        self.status_event(event_id, occurred_at, CaseEventType::Resolved, actor_id, None, notes)
    }

    pub fn escalate(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Acknowledged | CaseStatus::FollowUp | CaseStatus::InProgress | CaseStatus::Responded) {
            return Err(DomainError::InvalidOperation("Case is not ready for escalation"));
        }
        self.status = CaseStatus::Escalated;
        self.status_event(event_id, occurred_at, CaseEventType::Escalated, actor_id, None, notes)
    }

    pub fn close(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if !matches!(self.status, CaseStatus::Resolved | CaseStatus::Escalated) {
            return Err(DomainError::InvalidOperation("Only resolved or escalated cases can be closed"));
        }
        self.status = CaseStatus::Closed;
        self.status_event(event_id, occurred_at, CaseEventType::Closed, actor_id, None, notes)
    }

    pub fn add_evidence(
        &mut self,
        evidence_id: impl Into<String>,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if matches!(self.status, CaseStatus::Closed | CaseStatus::Archived) {
            return Err(DomainError::InvalidOperation("Cannot add evidence to a closed or archived case"));
        }
        let evidence_id = evidence_id.into();
        if !self.evidence_refs.contains(&evidence_id) {
            self.evidence_refs.push(evidence_id.clone());
        }
        self.status_event(event_id, occurred_at, CaseEventType::EvidenceAdded, actor_id, source_channel, Some(evidence_id))
    }

    pub fn add_document(
        &mut self,
        document_id: impl Into<String>,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if self.status == CaseStatus::Archived {
            return Err(DomainError::InvalidOperation("Cannot add a document to an archived case"));
        }
        let document_id = document_id.into();
        if !self.document_refs.contains(&document_id) {
            self.document_refs.push(document_id.clone());
        }
        self.status_event(event_id, occurred_at, CaseEventType::DocumentAdded, actor_id, source_channel, Some(document_id))
    }

    pub fn correct(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        if matches!(self.status, CaseStatus::Closed | CaseStatus::Archived) {
            return Err(DomainError::InvalidOperation("Closed or archived cases cannot be corrected"));
        }
        self.status_event(event_id, occurred_at, CaseEventType::Correction, actor_id, None, notes)
    }

    pub fn confirmed_delivery(&self) -> bool {
        confirmed_delivery(self.status)
    }

    fn ensure_content(&self) -> Result<(), DomainError> {
        if self.subject.trim().is_empty() || self.narrative.trim().is_empty() {
            return Err(DomainError::InvalidOperation("A case requires a subject and narrative"));
        }
        Ok(())
    }

    fn ensure_editable(&self) -> Result<(), DomainError> {
        if matches!(
            self.status,
            CaseStatus::Submitting
                | CaseStatus::Queued
                | CaseStatus::Submitted
                | CaseStatus::Acknowledged
                | CaseStatus::InProgress
                | CaseStatus::Responded
                | CaseStatus::Resolved
                | CaseStatus::Escalated
                | CaseStatus::Closed
                | CaseStatus::Archived
        ) {
            return Err(DomainError::InvalidOperation("Case is no longer editable"));
        }
        Ok(())
    }

    fn require_status(&self, expected: CaseStatus, message: &'static str) -> Result<(), DomainError> {
        if self.status != expected {
            return Err(DomainError::InvalidOperation(message));
        }
        Ok(())
    }

    fn status_event(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        event_type: CaseEventType,
        actor_id: Option<String>,
        source_channel: Option<String>,
        source_ref: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        let mut event = CaseEvent::new(event_id, self.case_id.clone(), event_type, occurred_at);
        event.actor_id = actor_id;
        event.source_channel = source_channel;
        event.source_ref = source_ref;
        self.record(event)
    }

    fn record(&mut self, event: CaseEvent) -> Result<CaseEvent, DomainError> {
        if event.case_id != self.case_id {
            return Err(DomainError::EventBelongsToDifferentCase);
        }
        if self.events.iter().any(|existing| existing.event_id == event.event_id) {
            return Err(DomainError::DuplicateEventId);
        }
        self.events.push(event.clone());
        Ok(event)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DomainError {
    InvalidOperation(&'static str),
    ConsentRequired,
    EventBelongsToDifferentCase,
    DuplicateEventId,
    InvalidTransition { from: CaseStatus, to: CaseStatus },
}

impl CaseStatus {
    pub fn can_transition(self, target: Self) -> bool {
        use CaseStatus::*;
        match self {
            Draft => matches!(target, Review),
            Review => matches!(target, Review | Ready),
            Ready => matches!(target, Ready | Submitting),
            Submitting => matches!(target, Submitting | Queued | Submitted),
            Queued => matches!(target, Queued | Submitted),
            Submitted => matches!(target, Acknowledged),
            Acknowledged => matches!(target, FollowUp | InProgress | Responded | Escalated),
            FollowUp => matches!(target, FollowUp | Responded | Escalated),
            InProgress => matches!(target, FollowUp | Responded | Escalated),
            Responded => matches!(target, FollowUp | Resolved | Escalated),
            Resolved => matches!(target, Closed),
            Escalated => matches!(target, Responded | Closed),
            Closed => matches!(target, Archived),
            Archived => false,
        }
    }

    pub fn require_transition(self, target: Self) -> Result<(), DomainError> {
        if self.can_transition(target) {
            Ok(())
        } else {
            Err(DomainError::InvalidTransition { from: self, to: target })
        }
    }

    pub fn confirmed_delivery(self) -> bool {
        confirmed_delivery(self)
    }
}

pub fn confirmed_delivery(status: CaseStatus) -> bool {
    matches!(
        status,
        CaseStatus::Acknowledged
            | CaseStatus::FollowUp
            | CaseStatus::InProgress
            | CaseStatus::Responded
            | CaseStatus::Resolved
            | CaseStatus::Escalated
            | CaseStatus::Closed
    )
}

pub fn validate_event_chain<I>(events: I) -> bool
where
    I: IntoIterator<Item = CaseEvent>,
{
    let mut previous: Option<CaseEventType> = None;
    let mut seen = std::collections::HashSet::new();
    let mut case_id: Option<String> = None;

    for event in events {
        if case_id.is_none() {
            case_id = Some(event.case_id.clone());
        }
        if Some(&event.case_id) != case_id.as_ref() || !seen.insert(event.event_id.clone()) {
            return false;
        }
        if previous == Some(CaseEventType::Acknowledged) && event.event_type == CaseEventType::Submitted {
            return false;
        }
        if previous == Some(CaseEventType::Closed) {
            return false;
        }
        previous = Some(event.event_type);
    }
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_case() -> CivicCase {
        let mut case = CivicCase::new(
            "case-1",
            CaseType::Complaint,
            "Delayed public service",
            "The requested service has not been delivered.",
        );
        case.consent_refs.push("consent-1".into());
        case.start_review("event-1", "2026-08-24T00:00:00Z", None).unwrap();
        case.mark_ready("event-2", "2026-08-24T00:01:00Z", None).unwrap();
        case
    }

    #[test]
    fn aggregate_preserves_canonical_fields_and_lifecycle() {
        let mut case = make_case();
        case.jurisdiction.insert("district".into(), "Bengaluru Urban".into());
        case.related_official_id = Some("official-1".into());
        case.begin_submission("event-3", "2026-08-24T00:02:00Z", None, None).unwrap();
        case.submit("event-4", "2026-08-24T00:03:00Z", None, None).unwrap();
        case.acknowledge("event-5", "2026-08-24T00:04:00Z", None, Some("web".into()), Some("ACK-1".into()), None).unwrap();
        assert_eq!(case.status, CaseStatus::Acknowledged);
        assert!(case.confirmed_delivery());
        assert_eq!(case.events.len(), 5);
    }

    #[test]
    fn consent_gate_is_enforced() {
        let mut case = CivicCase::new("case-1", CaseType::Complaint, "Subject", "Narrative");
        case.start_review("event-1", "2026-08-24T00:00:00Z", None).unwrap();
        assert_eq!(
            case.mark_ready("event-2", "2026-08-24T00:01:00Z", None),
            Err(DomainError::ConsentRequired)
        );
    }

    #[test]
    fn duplicate_and_cross_case_events_are_rejected() {
        let mut case = make_case();
        assert!(matches!(
            case.begin_submission("event-1", "2026-08-24T00:02:00Z", None, None),
            Err(DomainError::DuplicateEventId)
        ));
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
        use CaseStatus::*;
        assert!(Draft.can_transition(Review));
        assert!(Acknowledged.can_transition(InProgress));
        assert!(Closed.can_transition(Archived));
        assert!(!Submitted.confirmed_delivery());
        assert!(Acknowledged.confirmed_delivery());
        assert!(!Archived.confirmed_delivery());
    }

    #[test]
    fn serde_uses_contract_values() {
        assert_eq!(serde_json::to_string(&CaseType::TransferConcern).unwrap(), "\"transfer_concern\"");
        assert_eq!(serde_json::to_string(&CaseStatus::FollowUp).unwrap(), "\"follow_up\"");
        assert_eq!(serde_json::to_string(&CaseEventType::ReviewStarted).unwrap(), "\"review_started\"");
    }
}
