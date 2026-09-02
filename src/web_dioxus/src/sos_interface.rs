use crate::decentralized_drivers::JanavaniDecentralizedCore;
use serde::{Deserialize, Serialize};
use web_sys::window;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LocalEmergencyContext {
    pub tracking_id: String,
    pub geo_coordinates: String,
    pub danger_context: String,
}

pub struct JanavaniWasmSOSTrigger;

impl JanavaniWasmSOSTrigger {
    /// Dispatches an emergency event through an available transport adapter.
    /// This is a capability scaffold; it does not guarantee delivery to responders.
    pub async fn dispatch_panic_beacon(
        context: LocalEmergencyContext,
    ) -> Result<String, String> {
        let is_online = window()
            .navigator()
            .on_line();
        let raw_payload = format!(
            "JANAVANI SOS ALERT | TYPE: {} | LOC: {} | ID: {}",
            context.danger_context, context.geo_coordinates, context.tracking_id
        );

        if !is_online {
            let mesh_id = JanavaniDecentralizedCore::transmit_via_reticulum_mesh(&raw_payload)?;
            return Ok(format!(
                "Offline transport capability scaffold invoked: {mesh_id}"
            ));
        }

        Err("Emergency backend transport is not configured for this client.".to_string())
    }

    /// Clears only Janavani-owned local browser records.
    /// It must never erase unrelated application or browser data.
    pub fn local_emergency_device_wipe() -> Result<(), String> {
        let storage = window()
            .local_storage()
            .map_err(|_| "Storage access denied.")?
            .ok_or_else(|| "Local storage unavailable.")?;
        let mut keys = Vec::new();

        for index in 0..storage.length().unwrap_or(0) {
            if let Some(key) = storage
                .key(index)
                .map_err(|_| "Storage key lookup failed.")?
            {
                if key.starts_with("local_doc:") {
                    keys.push(key);
                }
            }
        }

        for key in keys {
            storage
                .remove_item(&key)
                .map_err(|_| "Wipe operation failed.")?;
        }
        Ok(())
    }
}
