use serde::{Deserialize, Serialize};
use crate::decentralized_drivers::JanavaniDecentralizedCore;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LocalEmergencyContext {
    pub tracking_id: String,
    pub geo_coordinates: String,
    pub danger_context: String,
}

pub struct JanavaniWasmSOSTrigger;

impl JanavaniWasmSOSTrigger {
    /// Dispatches an emergency request only through explicitly configured and
    /// verified transports. A successful HTTP response means backend acceptance,
    /// not confirmed emergency delivery.
    pub async fn dispatch_panic_beacon(context: LocalEmergencyContext) -> Result<String, String> {
        if context.geo_coordinates.trim().is_empty() {
            return Err("Emergency location is unavailable; no location was fabricated.".to_string());
        }

        let nav = gloo_utils::window().navigator();
        let is_online = nav.on_line();
        let raw_payload = format!(
            "🚨 JANAVANI SOS ALERT | TYPE: {} | LOC: {} | ID: {}",
            context.danger_context, context.geo_coordinates, context.tracking_id
        );

        if !is_online {
            return JanavaniDecentralizedCore::transmit_via_reticulum_mesh(&raw_payload)
                .map_err(|e| format!("Reticulum capability unavailable: {}", e.capability));
        }

        let backend_url = option_env!("JANAVANI_SOS_BACKEND_URL")
            .ok_or_else(|| "SOS backend is not configured for this client build.".to_string())?;
        let interface_token = option_env!("JANAVANI_SOS_INTERFACE_TOKEN")
            .ok_or_else(|| "SOS interface credential is not configured for this client build.".to_string())?;

        let client = reqwest::Client::new();
        let response = client
            .post(backend_url)
            .header("X-Janavani-Interface-Token", interface_token)
            .json(&serde_json::json!({
                "session_tracking_id": context.tracking_id,
                "approximate_coordinates": context.geo_coordinates,
                "danger_context": context.danger_context,
            }))
            .send()
            .await
            .map_err(|e| format!("Emergency backend connection failed: {e}"))?;

        if response.status().is_success() {
            Ok("Emergency request accepted by the configured backend; delivery is not yet confirmed.".to_string())
        } else {
            Err(format!("Emergency backend rejected the request with status {}", response.status()))
        }
    }

    /// Explicitly clears browser local storage. This is not described as a
    /// remote/global wipe and is not invoked automatically after dispatch.
    pub fn local_emergency_device_wipe() -> Result<(), String> {
        let storage = gloo_utils::window()
            .local_storage()
            .map_err(|_| "Storage access denied.")?
            .ok_or_else(|| "Local storage space unavailable.")?;
        storage.clear().map_err(|_| "Local storage wipe failed.")?;
        Ok(())
    }
}
