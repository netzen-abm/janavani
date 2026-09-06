use serde::{Deserialize, Serialize};

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
            return Err("scope must not be empty for required consent");
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
        self.is_authorized()
            && self.purpose == purpose
            && self.scope.iter().any(|item| item == scope)
    }
}
