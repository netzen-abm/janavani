#[cfg(test)]
mod tests {
    use crate::dynamic_directory::{DioxusDirectoryParser, NostrDirectoryEvent, DynamicMunicipalProfile};

    #[test]
    fn test_dynamic_directory_verified_parsing() {
        let trusted_signer = "npub1janavani789xxyz0123456789abcdef0123456789abcdef012".to_string();
        let trusted_list = vec![trusted_signer.clone()];
        
        let sample_profile = DynamicMunicipalProfile {
            state: "Kerala".to_string(),
            district: "Kozhikode".to_string(),
            local_body_type: "Corporation".to_string(),
            administrative_head_designation: "The Secretary".to_string(),
            official_vernacular_language: "Malayalam".to_string(),
            primary_postal_address: "Kozhikode, Kerala".to_string(),
        };

        let raw_content = serde_json::to_string(&sample_profile).unwrap();
        let mock_event = NostrDirectoryEvent {
            pubkey: trusted_signer,
            content: raw_content,
            sig: "a".repeat(128),
            id: "b".repeat(64),
        };

        let parse_result = DioxusDirectoryParser::parse_and_verify_update(mock_event, &trusted_list);
        
        assert!(parse_result.is_ok());
        let (geo_key, profile_data) = parse_result.unwrap();
        assert_eq!(geo_key, "DYNAMIC-KERALA-KOZHIKODE");
        assert_eq!(profile_data.official_vernacular_language, "Malayalam");
    }

    #[test]
    fn test_dynamic_directory_untrusted_signer_rejection() {
        let untrusted_list = vec!["npub1janavani789xxyz0123456789abcdef0123456789abcdef012".to_string()];
        
        let mock_event = NostrDirectoryEvent {
            pubkey: "npub1untrustedattackerkeyhere0123456789abcdef0123456789abcdef01".to_string(),
            content: "{}".to_string(),
            sig: "a".repeat(128),
            id: "b".repeat(64),
        };

        let parse_result = DioxusDirectoryParser::parse_and_verify_update(mock_event, &untrusted_list);
        assert!(parse_result.is_err());
    }
}
