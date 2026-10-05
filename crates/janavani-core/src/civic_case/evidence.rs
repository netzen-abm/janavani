use super::*;

impl CivicCase {
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        let evidence_id = evidence_id.into();
        if !self.evidence_refs.contains(&evidence_id) { self.evidence_refs.push(evidence_id.clone()); }
        self.status_event(event_id, occurred_at, CaseEventType::EvidenceAdded, actor_id, source_channel, Some(evidence_id), None)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        let document_id = document_id.into();
        if !self.document_refs.contains(&document_id) { self.document_refs.push(document_id.clone()); }
        self.status_event(event_id, occurred_at, CaseEventType::DocumentAdded, actor_id, source_channel, Some(document_id), None)
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
        let event_id = event_id.into();
        self.ensure_event_id_available(&event_id)?;
        self.status_event(event_id, occurred_at, CaseEventType::Correction, actor_id, None, None, notes)
    }

}
