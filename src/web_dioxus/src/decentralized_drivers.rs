//! Optional decentralized-provider capability boundary.
//!
//! This module deliberately does not simulate successful Nostr, Nym,
//! Reticulum, or blockchain operations. Provider integrations must be added
//! behind these explicit boundaries and return observed, attributable results.

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct DecentralizedStatusGrid {
    pub nostr_active: bool,
    pub nym_active: bool,
    pub reticulum_active: bool,
    pub blockchain_active: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ProviderAvailability {
    Available,
    Unavailable,
}

pub struct JanavaniDecentralizedCore;

impl JanavaniDecentralizedCore {
    pub fn status() -> DecentralizedStatusGrid {
        DecentralizedStatusGrid::default()
    }

    pub fn nostr_status() -> ProviderAvailability {
        ProviderAvailability::Unavailable
    }

    pub fn nym_status() -> ProviderAvailability {
        ProviderAvailability::Unavailable
    }

    pub fn reticulum_status() -> ProviderAvailability {
        ProviderAvailability::Unavailable
    }

    pub fn blockchain_status() -> ProviderAvailability {
        ProviderAvailability::Unavailable
    }

    /// Returns an explicit unavailable state until a real Reticulum/RNS
    /// provider is configured. No fake packet ID is generated.
    pub fn transmit_via_reticulum_mesh(_document_text: &str) -> Result<String, String> {
        Err("Reticulum provider is unavailable".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decentralized_providers_are_not_reported_as_active_without_adapters() {
        let status = JanavaniDecentralizedCore::status();
        assert!(!status.nostr_active);
        assert!(!status.nym_active);
        assert!(!status.reticulum_active);
        assert!(!status.blockchain_active);
    }

    #[test]
    fn reticulum_does_not_fabricate_success() {
        assert_eq!(
            JanavaniDecentralizedCore::transmit_via_reticulum_mesh("test"),
            Err("Reticulum provider is unavailable".to_string())
        );
    }
}
