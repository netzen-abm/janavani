use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub struct DecentralizedStatusGrid {
    pub nostr_active: bool,
    pub nym_active: bool,
    pub reticulum_active: bool,
    pub blockchain_active: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum CapabilityState {
    Unavailable,
    Configured,
    Verified,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CapabilityUnavailable {
    pub capability: &'static str,
    pub reason: &'static str,
}

pub struct JanavaniDecentralizedCore;

impl JanavaniDecentralizedCore {
    /// Nostr identity must be supplied by a real key-management implementation.
    /// This client adapter deliberately does not generate or invent a private key.
    pub fn initialize_nostr_identity() -> Result<(String, String), CapabilityUnavailable> {
        Err(CapabilityUnavailable {
            capability: "nostr",
            reason: "no verified WASM key-management adapter is wired in this client",
        })
    }

    /// Nym routing is unavailable until a real Nym client/transport adapter is wired.
    pub async fn route_via_nym_mixnet(
        _target_url: &str,
        _payload: &str,
    ) -> Result<String, CapabilityUnavailable> {
        Err(CapabilityUnavailable {
            capability: "nym",
            reason: "no verified Nym transport adapter is wired in this client",
        })
    }

    /// Reticulum transmission is unavailable until a real RNS adapter is wired.
    pub fn transmit_via_reticulum_mesh(
        _document_text: &str,
    ) -> Result<String, CapabilityUnavailable> {
        Err(CapabilityUnavailable {
            capability: "reticulum",
            reason: "no verified Reticulum transport adapter is wired in this client",
        })
    }

    /// A Merkle-root shape check is not proof verification. Do not report it as such.
    pub fn verify_blockchain_compliance_checkpoint(
        _merkle_root: &str,
    ) -> Result<bool, CapabilityUnavailable> {
        Err(CapabilityUnavailable {
            capability: "blockchain_zkp",
            reason: "no verified proof-verification adapter is wired in this client",
        })
    }
}
