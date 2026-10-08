use super::*;

impl CivicCase {
    pub fn confirmed_delivery(&self) -> bool { confirmed_delivery(self.status) }

    fn ensure_content(&self) -> Result<(), DomainError> {
        if self.subject.trim().is_empty() || self.narrative.trim().is_empty() {
            return Err(DomainError::InvalidOperation("A case requires a subject and narrative"));
        }
        Ok(())
    }

    fn ensure_editable(&self) -> Result<(), DomainError> {
        if matches!(self.status, CaseStatus::Submitting | CaseStatus::Queued | CaseStatus::Submitted | CaseStatus::Acknowledged | CaseStatus::InProgress | CaseStatus::Responded | CaseStatus::Resolved | CaseStatus::Escalated | CaseStatus::Closed | CaseStatus::Archived) {
            return Err(DomainError::InvalidOperation("Case is no longer editable"));
        }
        Ok(())
    }

    fn ensure_event_id_available(&self, event_id: &str) -> Result<(), DomainError> {
        if self.events.iter().any(|event| event.event_id == event_id) { return Err(DomainError::DuplicateEventId); }
        Ok(())
    }

    fn require_status(&self, expected: CaseStatus, message: &'static str) -> Result<(), DomainError> {
        if self.status != expected { return Err(DomainError::InvalidOperation(message)); }
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
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        let mut event = CaseEvent::new(event_id, self.case_id.clone(), event_type, occurred_at);
        event.actor_id = actor_id;
        event.source_channel = source_channel;
        event.source_ref = source_ref;
        event.notes = notes;
        self.record(event)
    }

    fn record(&mut self, event: CaseEvent) -> Result<CaseEvent, DomainError> {
        if event.case_id != self.case_id { return Err(DomainError::EventBelongsToDifferentCase); }
        if self.events.iter().any(|existing| existing.event_id == event.event_id) { return Err(DomainError::DuplicateEventId); }
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
            Ready => matches!(target, Ready | Submitting | Submitted),
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
        if self.can_transition(target) { Ok(()) } else { Err(DomainError::InvalidTransition { from: self, to: target }) }
    }

    pub fn confirmed_delivery(self) -> bool { confirmed_delivery(self) }
}

pub fn confirmed_delivery(status: CaseStatus) -> bool {
    matches!(status, CaseStatus::Acknowledged | CaseStatus::FollowUp | CaseStatus::InProgress | CaseStatus::Responded | CaseStatus::Resolved | CaseStatus::Escalated | CaseStatus::Closed)
}

pub fn validate_event_chain<I>(events: I) -> bool
where
    I: IntoIterator<Item = CaseEvent>,
{
    let mut previous: Option<CaseEventType> = None;
    let mut seen = std::collections::HashSet::new();
    let mut case_id: Option<String> = None;

    for event in events {
        if case_id.is_none() { case_id = Some(event.case_id.clone()); }
        if Some(&event.case_id) != case_id.as_ref() || !seen.insert(event.event_id.clone()) { return false; }
        if previous == Some(CaseEventType::Acknowledged) && event.event_type == CaseEventType::Submitted { return false; }
        if previous == Some(CaseEventType::Closed) { return false; }
        previous = Some(event.event_type);
    }
    true
}


