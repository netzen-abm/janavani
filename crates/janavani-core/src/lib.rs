//! Canonical, channel-neutral Janavani domain kernel.
//!
//! This crate contains the CivicCase aggregate, event model, lifecycle
//! contract, and consent domain. It intentionally contains no database,
//! Telegram, HTTP, AI, or UI dependencies.

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

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConsentGrantType {
    Explicit,
    RequiredByDestination,
    NotRequired,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConsentStatus {
    Granted,
    Denied,
    Revoked,
    Expired,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Consent {
    pub consent_id: String,
    pub subject_id: String,
    pub purpose: String,
    pub scope: Vec<String>,
    pub grant_type: ConsentGrantType,
    pub status: ConsentStatus,
    pub created_at: String,
    pub expires_at: Option<String>,
    pub revoked_at: Option<String>,
    pub proof_ref: Option<String>,
}

impl Consent {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.consent_id.trim().is_empty() {
            return Err("consent_id must not be empty");
        }
        if self.subject_id.trim().is_empty() {
            return Err("subject_id must not be empty");
        }
        if self.purpose.trim().is_empty() {
            return Err("purpose must not be empty");
        }
        if self.scope.is_empty() && self.grant_type != ConsentGrantType::NotRequired {
            return Err("scope must not be empty for granted consent");
        }
        if self.created_at.trim().is_empty() {
            return Err("created_at must not be empty");
        }
        if self.status == ConsentStatus::Revoked && self.revoked_at.is_none() {
            return Err("revoked_at is required for revoked consent");
        }
        Ok(())
    }

    pub fn is_authorized(&self) -> bool {
        self.status == ConsentStatus::Granted
    }

    pub fn authorizes(&self, purpose: &str, scope: &str) -> bool {
        self.is_authorized() && self.purpose == purpose && self.scope.iter().any(|item| item == scope)
    }
}

// CivicCase and lifecycle implementation continue below.
