//! Canonical, channel-neutral Janavani domain kernel.
//!
//! This crate contains the CivicCase aggregate, event model, and lifecycle
//! contract. It intentionally contains no database, Telegram, HTTP, AI, or UI
//! dependencies.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

pub type JsonObject = BTreeMap<String, Value>;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CaseType {
    Complaint,
    Grievance,
    Rti,
    Petition,
    Representation,
    Objection,
    NonConsent,
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
    CitizenVerified,
    CitizenReopened,
    SentByCitizen,
    ResponseReceived,
    NoResponseReported,
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
    pub jurisdiction: JsonObject,
    pub related_organisation_id: Option<String>,
    pub related_office_id: Option<String>,
    pub related_official_id: Option<String>,
    pub related_representative_id: Option<String>,
    pub claims: Vec<JsonObject>,
    pub evidence_refs: Vec<String>,
    pub document_refs: Vec<String>,
    pub consent_refs: Vec<String>,
    pub status: CaseStatus,
    pub events: Vec<CaseEvent>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
    pub version: u64,
}

mod draft;
mod evidence;
mod invariants;
mod outcomes;
mod submission;

#[cfg(test)]
mod tests;

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

}
