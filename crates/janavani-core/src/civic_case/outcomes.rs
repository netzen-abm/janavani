use super::*;

impl CivicCase {
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::FollowUp;
        self.status_event(event_id, occurred_at, CaseEventType::FollowUp, actor_id, None, None, notes)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Responded;
        self.status_event(event_id, occurred_at, CaseEventType::Response, actor_id, None, None, notes)
    }

    pub fn resolve(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Responded, "Only a responded case can be resolved")?;
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Resolved;
        self.status_event(event_id, occurred_at, CaseEventType::Resolved, actor_id, None, None, notes)
    }

    pub fn verify_resolution(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
        source_ref: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Resolved, "Only a resolved case can be citizen-verified")?;
        self.status_event(event_id, occurred_at, CaseEventType::CitizenVerified, actor_id, source_channel, source_ref, notes)
    }

    pub fn reopen_after_citizen_verification(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
        notes: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Resolved, "Only a resolved case can be reopened")?;
        self.status = CaseStatus::FollowUp;
        self.status_event(event_id, occurred_at, CaseEventType::CitizenReopened, actor_id, source_channel, None, notes)
    }

    pub fn citizen_verified_resolution(&self) -> bool {
        self.events.iter().any(|event| event.event_type == CaseEventType::CitizenVerified && event.source_ref.is_some())
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Escalated;
        self.status_event(event_id, occurred_at, CaseEventType::Escalated, actor_id, None, None, notes)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Closed;
        self.status_event(event_id, occurred_at, CaseEventType::Closed, actor_id, None, None, notes)
    }

}
