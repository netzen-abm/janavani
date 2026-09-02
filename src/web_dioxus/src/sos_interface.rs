use serde::{Serialize, Deserialize};
use web_sys::window;
use crate::decentralized_drivers::JanavaniDecentralizedCore;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LocalEmergencyContext {
    pub tracking_id: String,
    pub geo_coordinates: String,
    pub danger_context: String, // e.g., "Network Offline / Stalker Scenario / Unsafe Travel"
}

pub struct JanavaniWasmSOSTrigger;

impl JanavaniWasmSOSTrigger {
    /// Dispatches emergency distress events dynamically across available network mediums.
    pub async fn dispatch_panic_beacon(context: LocalEmergencyContext) -> Result<String, String> {
        let nav = gloo_utils::window().navigator();
        let is_online = nav.on_line();

        // Standardize the emergency string block format
        let raw_payload = format!(
            "🚨 JANAVANI SOS ALERT | TYPE: {} | LOC: {} | ID: {}", 
            context.danger_context, context.geo_coordinates, context.tracking_id
        );

        if !is_online {
            // --- OFFLINE AD-HOC COMMUNICATIONS MESH VECTOR (RETICULUM) ---
            // If network architecture drops completely, bypass internet routes and use ad-hoc channels.
            match JanavaniDecentralizedCore::transmit_via_reticulum_mesh(&raw_payload) {
                Ok(mesh_id) => {
                    // Wipe local browser state caches immediately to safeguard privacy on device loss
                    let _ = Self::local_emergency_device_wipe();
                    return Ok(format!("Offline Mesh Broadcast Active over Reticulum. Token Hash: {}", mesh_id));
                },
                Err(e) => return Err(format!("Mesh interface hardware failure: {}", e)),
            }
        }

        // --- ONLINE DISPATCH PATHWAY (HTTPS BACKEND RE-ROUTING) ---
        let client = reqwest::Client::new();
        let backend_url = "https://janavani.internal";

        let response = client.post(backend_url)
            .header("X-Janavani-Interface-Token", "web-mvp-token-abc")
            .json(&serde_json::json!({
                "session_tracking_id": context.tracking_id,
                "approximate_coordinates": context.geo_coordinates
            }))
            .send()
            .await
            .map_err(|e| format!("Emergency backend connection dropped: {}", e))?;

        if response.status().is_success() {
            let _ = Self::local_emergency_device_wipe();
            Ok("Online emergency routing complete. Cache wiped globally.".to_string())
        } else {
            Err(format!("Emergency server response failure code: {}", response.status()))
        }
    }

    /// Destroys all sensitive session data on the local device instantly.
    pub fn local_emergency_device_wipe() -> Result<(), String> {
        let storage = gloo_utils::window().local_storage()
            .map_err(|_| "Storage access denied.")?
            .ok_or_else(|| "Local storage space unavailable.")?;
            
        // Flash clear everything to prevent post-incident device extraction risks
        storage.clear().map_err(|_| "Wipe operations aborted.")?;
        Ok(())
    }
}
