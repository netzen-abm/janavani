use serde::{Serialize, Deserialize};
use crate::protocols::reticulum::ReticulumMeshDriver;
use crate::protocols::nym::NymMixnetDriver;

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum ActiveTransportRoute {
    NymEncryptedMixnet,
    StandardHttpsJitter,
    ReticulumAdHocMesh,
}

pub struct InvisibleNetworkMiddleware;

impl InvisibleNetworkMiddleware {
    /// Detects device connection profiles automatically to verify if a local Nym proxy loop is active.
    pub async fn check_local_nym_proxy_status() -> bool {
        let client = reqwest::Client::new();
        // Look up the default internal configuration port of a running Nym local client proxy
        let nym_check_url = "http://127.0.0";
        
        match client.get(nym_check_url).timeout(std::time::Duration::from_millis(500)).send().await {
            Ok(res) => res.status().is_success(),
            Err(_) => false,
        }
    }

    /// Dispatches citizen transaction payloads automatically over the most secure available transport medium.
    pub async fn auto_route_payload(endpoint_url: &str, json_payload: &str) -> Result<(ActiveTransportRoute, String), String> {
        let nav = gloo_utils::window().navigator();
        let is_internet_available = nav.on_line();

        // --- PATHWAY A: NO INTERNET CONNECTIVITY (RETICULUM RADIO MESH FALLBACK) ---
        if !is_internet_available {
            match ReticulumMeshDriver::broadcast_over_radio_frequencies(json_payload) {
                Ok(mesh_tx_hash) => return Ok((ActiveTransportRoute::ReticulumAdHocMesh, mesh_tx_hash)),
                Err(e) => return Err(format!("Total Network Disconnect: Reticulum mesh hardware fail: {}", e)),
            }
        }

        // --- PATHWAY B: INTERNET ACTIVE + LOCAL NYM MIXNET RUNNING ---
        if Self::check_local_nym_proxy_status().await {
            match NymMixnetDriver::tunnel_request_without_metadata(endpoint_url, json_payload).await {
                Ok(response_body) => return Ok((ActiveTransportRoute::NymEncryptedMixnet, response_body)),
                Err(_) => { /* Fall back to standard route if tunnel breaks unexpectedly */ }
            }
        }

        // --- PATHWAY C: STANDARD ENCRYPTED HTTPS ROUTE WITH RANDOM TIME JITTER ---
        let client = reqwest::Client::new();
        
        // Execute a brief, random runtime execution pause to scramble external traffic timing analysis
        # [cfg(target_arch = "wasm32")]
        {
            let random_delay_ms = (js_sys::Math::random() * 1500.0 + 500.0) as u64;
            let promise = js_sys::Promise::new(&mut |resolve, _| {
                gloo_utils::window().set_timeout_with_callback_and_timeout_and_arguments_0(
                    &resolve, random_delay_ms as i32
                ).unwrap();
            });
            let _ = wasm_bindgen_futures::JsFuture::from(promise).await;
        }

        match client.post(endpoint_url)
            .header("X-Janavani-Interface-Token", "web-v2-token")
            .header("Content-Type", "application/json")
            .body(json_payload.to_string())
            .send()
            .await 
        {
            Ok(res) => {
                if res.status().is_success() {
                    let body = res.text().await.unwrap_or_default();
                    Ok((ActiveTransportRoute::StandardHttpsJitter, body))
                } else {
                    Err(format!("Server interface returned a non-success code: {}", res.status()))
                }
            },
            Err(network_error) => Err(format!("HTTPS pipeline connection dropped: {}", network_error))
        }
    }
}
