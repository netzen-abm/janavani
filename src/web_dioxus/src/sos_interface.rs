//! Emergency capability boundary for the Web client.
//!
//! SOS transport must only report a real dispatch result. This module does
//! not manufacture delivery confirmations, provider IDs, or location data.

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct LocalEmergencyContext {
    pub tracking_id: String,
    pub geo_coordinates: Option<String>,
    pub danger_context: String,
}

pub struct JanavaniWasmSOSTrigger;

impl JanavaniWasmSOSTrigger {
    /// Returns an explicit unavailable result until a real SOS transport
    /// adapter is configured.
    pub async fn dispatch_panic_beacon(_context: LocalEmergencyContext) -> Result<String, String> {
        Err("SOS transport provider is unavailable".to_string())
    }

    /// Clear only Janavani-owned browser records. This is intentionally not
    /// presented as a guaranteed forensic/device wipe.
    pub fn clear_janavani_local_storage() -> Result<(), String> {
        let storage = gloo_utils::window()
            .local_storage()
            .map_err(|_| "Storage access denied")?
            .ok_or_else(|| "Local storage unavailable".to_string())?;

        let length = storage.length().map_err(|_| "Unable to inspect local storage")?;
        let mut keys = Vec::new();
        for index in 0..length {
            if let Ok(Some(key)) = storage.key(index) {
                if key.starts_with("local_doc:") || key.starts_with("janavani:") {
                    keys.push(key);
                }
            }
        }

        for key in keys {
            storage
                .remove_item(&key)
                .map_err(|_| format!("Unable to clear local record: {key}"))?;
        }
        Ok(())
    }
}
