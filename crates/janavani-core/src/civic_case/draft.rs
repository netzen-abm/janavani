use super::*;

impl CivicCase {
    pub fn edit(
        &mut self,
        event_id: impl Into<String>,
        occurred_at: impl Into<String>,
        actor_id: Option<String>,
        subject: Option<String>,
        narrative: Option<String>,
    ) -> Result<CaseEvent, DomainError> {
        self.ensure_editable()?;
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
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
            return Err(DomainError::InvalidOperation(
                "Only a draft case can enter review",
            ));
        }
        self.ensure_content()?;
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Review;
        self.status_event(event_id, occurred_at, CaseEventType::ReviewStarted, actor_id, None, None, None)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status = CaseStatus::Ready;
        self.status_event(event_id, occurred_at, CaseEventType::Approved, actor_id, None, None, None)
    }

}
