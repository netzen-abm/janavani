#[cfg(test)]
mod tests {
    use crate::decentralized_drivers::JanavaniDecentralizedCore;

    #[test]
    fn test_nostr_is_not_reported_as_verified_without_adapter() {
        let result = JanavaniDecentralizedCore::initialize_nostr_identity();
        assert!(result.is_err());
        let error = result.unwrap_err();
        assert_eq!(error.capability, "nostr");
    }

    #[test]
    fn test_blockchain_verification_is_not_faked() {
        let valid_merkle_root = "0x8f3c2d1e9b4a5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d";
        let invalid_root = "broken-non-hex-string-format";

        let valid_result = JanavaniDecentralizedCore::verify_blockchain_compliance_checkpoint(valid_merkle_root);
        let invalid_result = JanavaniDecentralizedCore::verify_blockchain_compliance_checkpoint(invalid_root);

        assert!(valid_result.is_err());
        assert!(invalid_result.is_err());
        assert_eq!(valid_result.unwrap_err().capability, "blockchain_zkp");
        assert_eq!(invalid_result.unwrap_err().capability, "blockchain_zkp");
    }
}
