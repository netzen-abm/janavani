//! Janavani decentralized capability boundary.
//!
//! Protocol features remain independently selectable. A feature being enabled
//! means its dependency is available to the build; it does not claim that the
//! real network capability is operational. Until a verified adapter exists,
//! operations return an explicit unavailable result rather than synthetic
//! success.

use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CapabilityUnavailable {
    pub capability: &'static str,
    pub reason: &'static str,
}

impl fmt::Display for CapabilityUnavailable {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} capability unavailable: {}", self.capability, self.reason)
    }
}

impl std::error::Error for CapabilityUnavailable {}

#[cfg(feature = "nostr")]
pub mod janavani_nostr {
    use super::CapabilityUnavailable;

    pub struct NostrBridge;

    impl NostrBridge {
        pub fn init_identity() -> Result<(), CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "nostr",
                reason: "real key-management and relay adapter is not yet wired",
            })
        }
    }
}

#[cfg(feature = "nym")]
pub mod janavani_nym {
    use super::CapabilityUnavailable;

    pub struct NymPrivacyLayer;

    impl NymPrivacyLayer {
        pub fn send_anonymous_packet(_payload: Vec<u8>) -> Result<(), CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "nym",
                reason: "real Nym transport adapter is not yet wired",
            })
        }
    }
}

#[cfg(feature = "reticulum")]
pub mod janavani_reticulum {
    use super::CapabilityUnavailable;

    pub struct ReticulumMesh;

    impl ReticulumMesh {
        pub fn broadcast_off_grid(_data: &[u8]) -> Result<(), CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "reticulum",
                reason: "real Reticulum transport adapter is not yet wired",
            })
        }
    }
}

#[cfg(feature = "zkp")]
pub mod janavani_zkp {
    use super::CapabilityUnavailable;

    pub struct ResidencyVerifier;

    impl ResidencyVerifier {
        pub fn generate_membership_proof() -> Result<Vec<u8>, CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "zkp",
                reason: "real proof circuit, witness handling, and verifier are not yet wired",
            })
        }
    }
}

#[cfg(feature = "blockchain")]
pub mod janavani_blockchain {
    use super::CapabilityUnavailable;

    pub struct LedgerAnchor;

    impl LedgerAnchor {
        pub fn lock_grievance_hash(_hash: [u8; 32]) -> Result<(), CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "blockchain",
                reason: "real chain client, transaction submission, and confirmation are not yet wired",
            })
        }
    }
}

#[cfg(feature = "freenet")]
pub mod janavani_freenet {
    use super::CapabilityUnavailable;

    pub struct FreenetContract;

    impl FreenetContract {
        pub fn sync_shared_state() -> Result<(), CapabilityUnavailable> {
            Err(CapabilityUnavailable {
                capability: "freenet",
                reason: "real Contract/Delegate integration and network verification are not yet wired",
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::CapabilityUnavailable;

    #[test]
    fn unavailable_error_is_explicit() {
        let error = CapabilityUnavailable {
            capability: "example",
            reason: "adapter not wired",
        };
        assert_eq!(error.to_string(), "example capability unavailable: adapter not wired");
    }

    #[test]
    #[cfg(feature = "nostr")]
    fn nostr_does_not_fake_success() {
        let result = crate::janavani_nostr::NostrBridge::init_identity();
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "nostr");
    }

    #[test]
    #[cfg(feature = "nym")]
    fn nym_does_not_fake_success() {
        let result = crate::janavani_nym::NymPrivacyLayer::send_anonymous_packet(vec![1, 2, 3]);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "nym");
    }

    #[test]
    #[cfg(feature = "reticulum")]
    fn reticulum_does_not_fake_success() {
        let result = crate::janavani_reticulum::ReticulumMesh::broadcast_off_grid(b"test");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "reticulum");
    }

    #[test]
    #[cfg(feature = "zkp")]
    fn zkp_does_not_return_dummy_proof() {
        let result = crate::janavani_zkp::ResidencyVerifier::generate_membership_proof();
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "zkp");
    }

    #[test]
    #[cfg(feature = "blockchain")]
    fn blockchain_does_not_fake_anchoring() {
        let result = crate::janavani_blockchain::LedgerAnchor::lock_grievance_hash([0u8; 32]);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "blockchain");
    }

    #[test]
    #[cfg(feature = "freenet")]
    fn freenet_does_not_fake_sync() {
        let result = crate::janavani_freenet::FreenetContract::sync_shared_state();
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().capability, "freenet");
    }
}
