//! Janavani decentralized capability contracts.
//!
//! These modules are interface boundaries only until real protocol adapters
//! are implemented and independently verified. They deliberately fail closed
//! rather than reporting simulated success as real capability.

#[cfg(feature = "nostr")]
pub mod janavani_nostr {
    pub struct NostrBridge;
    impl NostrBridge { pub fn init_identity() -> Result<(), &'static str> { Err("Nostr adapter is not implemented in this build") } }
}
#[cfg(feature = "nym")]
pub mod janavani_nym {
    pub struct NymPrivacyLayer;
    impl NymPrivacyLayer { pub fn send_anonymous_packet(_payload: Vec<u8>) -> Result<(), &'static str> { Err("Nym adapter is not implemented in this build") } }
}
#[cfg(feature = "reticulum")]
pub mod janavani_reticulum {
    pub struct ReticulumMesh;
    impl ReticulumMesh { pub fn broadcast_off_grid(_data: &[u8]) -> Result<(), &'static str> { Err("Reticulum adapter is not implemented in this build") } }
}
#[cfg(feature = "zkp")]
pub mod janavani_zkp {
    pub struct ResidencyVerifier;
    impl ResidencyVerifier { pub fn generate_membership_proof() -> Result<Vec<u8>, &'static str> { Err("ZKP verifier/prover is not implemented in this build") } }
}
#[cfg(feature = "blockchain")]
pub mod janavani_blockchain {
    pub struct LedgerAnchor;
    impl LedgerAnchor { pub fn lock_grievance_hash(_hash: [u8; 32]) -> Result<(), &'static str> { Err("Blockchain anchoring adapter is not implemented in this build") } }
}
#[cfg(feature = "freenet")]
pub mod janavani_freenet {
    pub struct FreenetContract;
    impl FreenetContract { pub fn sync_shared_state() -> Result<(), &'static str> { Err("Freenet adapter is not implemented in this build") } }
}
#[cfg(test)]
mod tests {
    #[test] #[cfg(feature = "nostr")] fn nostr_fails_closed() { assert!(super::janavani_nostr::NostrBridge::init_identity().is_err()); }
    #[test] #[cfg(feature = "nym")] fn nym_fails_closed() { assert!(super::janavani_nym::NymPrivacyLayer::send_anonymous_packet(vec![1]).is_err()); }
    #[test] #[cfg(feature = "reticulum")] fn reticulum_fails_closed() { assert!(super::janavani_reticulum::ReticulumMesh::broadcast_off_grid(b"test").is_err()); }
    #[test] #[cfg(feature = "zkp")] fn zkp_fails_closed() { assert!(super::janavani_zkp::ResidencyVerifier::generate_membership_proof().is_err()); }
    #[test] #[cfg(feature = "blockchain")] fn blockchain_fails_closed() { assert!(super::janavani_blockchain::LedgerAnchor::lock_grievance_hash([0u8; 32]).is_err()); }
    #[test] #[cfg(feature = "freenet")] fn freenet_fails_closed() { assert!(super::janavani_freenet::FreenetContract::sync_shared_state().is_err()); }
}
