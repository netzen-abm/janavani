//! Shared client/capability contract primitives.
//!
//! These types are deliberately presentation-neutral so Android, iOS, DApp,
//! Web and messaging adapters can consume the same capability semantics without
//! making one interface a dependency of another.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CapabilityState {
    Available,
    Degraded,
    DisabledByUser,
    DisabledByPolicy,
    Unavailable,
    Failed,
    NotConfigured,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CapabilityKind {
    CivicCase,
    Evidence,
    Document,
    GovernmentInformation,
    Submission,
    Tracking,
    Identity,
    PrivacyTransport,
    ResilientTransport,
    DecentralizedVerification,
    ArtificialIntelligence,
    Emergency,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CapabilityDescriptor {
    pub id: String,
    pub kind: CapabilityKind,
    pub state: CapabilityState,
    pub user_enabled: bool,
    pub requires_network: bool,
    pub requires_identity: bool,
    pub requires_external_provider: bool,
}

impl CapabilityDescriptor {
    pub fn is_usable(&self) -> bool {
        self.user_enabled
            && matches!(
                self.state,
                CapabilityState::Available | CapabilityState::Degraded
            )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DeliveryState {
    Created,
    Queued,
    Transmitting,
    Sent,
    Received,
    Acknowledged,
    Failed,
}

/// Delivery must never be inferred from a local transmission attempt.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DeliveryStatus {
    pub state: DeliveryState,
    pub transport: Option<String>,
    pub acknowledgement_reference: Option<String>,
}

impl DeliveryStatus {
    pub fn is_confirmed(&self) -> bool {
        matches!(self.state, DeliveryState::Received | DeliveryState::Acknowledged)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn capability_failure_does_not_imply_global_failure() {
        let descriptor = CapabilityDescriptor {
            id: "AI.RAG".into(),
            kind: CapabilityKind::ArtificialIntelligence,
            state: CapabilityState::Failed,
            user_enabled: true,
            requires_network: true,
            requires_identity: false,
            requires_external_provider: true,
        };

        assert!(!descriptor.is_usable());
        assert_eq!(descriptor.state, CapabilityState::Failed);
    }

    #[test]
    fn disabled_capability_is_not_usable() {
        let descriptor = CapabilityDescriptor {
            id: "WEB3.BLOCKCHAIN".into(),
            kind: CapabilityKind::DecentralizedVerification,
            state: CapabilityState::Available,
            user_enabled: false,
            requires_network: true,
            requires_identity: false,
            requires_external_provider: true,
        };

        assert!(!descriptor.is_usable());
    }

    #[test]
    fn sent_is_not_delivery_confirmation() {
        let status = DeliveryStatus {
            state: DeliveryState::Sent,
            transport: Some("internet".into()),
            acknowledgement_reference: None,
        };

        assert!(!status.is_confirmed());
    }

    #[test]
    fn acknowledgement_confirms_delivery() {
        let status = DeliveryStatus {
            state: DeliveryState::Acknowledged,
            transport: Some("internet".into()),
            acknowledgement_reference: Some("ACK-1".into()),
        };

        assert!(status.is_confirmed());
    }
}
