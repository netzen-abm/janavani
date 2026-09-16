//! Web surface adapter for the canonical Janavani SOS capability.
//!
//! This module intentionally contains no emergency policy, transport selection,
//! device wiping, mesh implementation, or provider credentials. The WebApp is
//! an access surface: it sends a user-authorised SOS request to the canonical
//! Janavani API and reports the server's truthful delivery state.

use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LocalEmergencyContext {
    pub tracking_id: String,
    pub geo_coordinates: Option<String>,
    pub danger_context: String,
    pub explicit_user_choice: bool,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
struct SosApiRequest {
    pub tracking_id: String,
    pub location_ref: Option<String>,
    pub incident_context: String,
    pub explicit_user_choice: bool,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
struct SosApiResponse {
    pub state: String,
    pub message: Option<String>,
}

pub struct JanavaniWasmSOSTrigger;

impl JanavaniWasmSOSTrigger {
    /// Submit a user-authorised SOS request through the canonical API boundary.
    ///
    /// The Web surface does not choose or execute emergency transports. Concrete
    /// delivery is owned by the server-side SOS capability and its adapters.
    pub async fn dispatch_panic_beacon(context: LocalEmergencyContext) -> Result<String, String> {
        if !context.explicit_user_choice {
            return Err("SOS requires explicit user choice before transmission.".to_string());
        }

        let endpoint = option_env!("JANAVANI_SOS_ENDPOINT")
            .or(option_env!("JANAVANI_BACKEND_URL"))
            .ok_or_else(|| {
                "No canonical Janavani SOS endpoint is configured for this WebApp environment.".to_string()
            })?;

        let url = if endpoint.ends_with("/api/v1/sos/trigger") {
            endpoint.to_string()
        } else {
            format!("{}/api/v1/sos/trigger", endpoint.trim_end_matches('/'))
        };

        let request = SosApiRequest {
            tracking_id: context.tracking_id,
            location_ref: context.geo_coordinates,
            incident_context: context.danger_context,
            explicit_user_choice: context.explicit_user_choice,
        };

        let response = Client::new()
            .post(url)
            .json(&request)
            .send()
            .await
            .map_err(|error| format!("Canonical SOS service connection failed: {error}"))?;

        if !response.status().is_success() {
            return Err(format!(
                "Canonical SOS service returned failure status: {}",
                response.status()
            ));
        }

        let result = response
            .json::<SosApiResponse>()
            .await
            .map_err(|error| format!("Canonical SOS response format mismatch: {error}"))?;

        match result.message {
            Some(message) => Ok(format!("SOS state: {} — {}", result.state, message)),
            None => Ok(format!("SOS state: {}", result.state)),
        }
    }
}
