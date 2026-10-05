use super::*;

impl CivicCase {
    pub fn begin_submission(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Ready, "Only a ready case can begin submission")?;
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Submitting;
        self.status_event(event_id, occurred_at, CaseEventType::Submitting, actor_id, source_channel, None, None)
    }

    pub fn queue_submission(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        source_channel: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.require_status(CaseStatus::Submitting, "Only a submitting case can be queued")?;
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Queued;
        self.status_event(event_id, occurred_at, CaseEventType::Queued, actor_id, source_channel, None, None)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Submitted;
        self.status_event(event_id, occurred_at, CaseEventType::Submitted, actor_id, source_channel, None, None)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Acknowledged;
        self.status_event(event_id, occurred_at, CaseEventType::Acknowledged, actor_id, source_channel, source_ref, notes)
    }

}
