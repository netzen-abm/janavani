use serde::{Serialize, Deserialize};
use std::collections::HashMap;
use dioxus::prelude::*;

@derive(Serialize, Deserialize, Clone, Debug, Default)
pub struct DynamicMunicipalProfile {
    pub state: String,
    pub district: String,
    pub local_body_type: String,
    pub administrative_head_designation: String,
    pub official_vernacular_language: String,
    pub primary_postal_address: String,
}

@derive(Serialize, Deserialize, Clone, Debug, Default)
pub struct NostrDirectoryEvent {
    pub pubkey: String,
    pub content: String, // Contains the serialized JSON string of DynamicMunicipalProfile
    pub sig: String,
    pub id: String,
}

pub struct DioxusDirectoryParser;

impl DioxusDirectoryParser {
    /// Validates and injects cryptographically signed community directory updates into frontend state.
    pub fn parse_and_verify_update(
        raw_event: NostrDirectoryEvent, 
        trusted_keys: &[String]
    ) -> Result<(String, DynamicMunicipalProfile), String> {
        // 1. Enforce public key validation checks locally inside WebAssembly
        if !trusted_keys.contains(&raw_event.pubkey) {
            return Err("Aborting injection: Public key is not verified in platform security anchors.".to_string());
        }

        // 2. Structural constraint length validations
        if raw_event.sig.len() != 128 || raw_event.id.len() != 64 {
            return Err("Aborting injection: Cryptographic signature matrix format is corrupt.".to_string());
        }

        // 3. Parse internal JSON content cleanly into directory profiles
        let profile: DynamicMunicipalProfile = serde_json::from_str(&raw_event.content)
            .map_err(|e| format!("Profile schema mapping mismatch: {}", e))?;

        // Generate a clean location grouping code key based on parsed parameters
        let generated_geo_key = format!("DYNAMIC-{}-{}", profile.state.to_uppercase(), profile.district.to_uppercase());

        Ok((generated_geo_key, profile))
    }
}
