use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ComplaintRequest {
    pub citizen_raw_input: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct DocumentPayload {
    pub subject_line: String,
    pub suggested_ministry_or_department: String,
    pub factual_points: Vec<String>,
    pub legal_or_policy_basis: Vec<String>,
    pub specific_prayers_or_requests: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct DraftResponse {
    pub status: String,
    pub tracking_id: String,
    pub document: DocumentPayload,
}

pub struct JanavaniDioxusBridge {
    pub backend_url: Option<String>,
    pub is_freenet_context: bool,
}

impl JanavaniDioxusBridge {
    pub fn new() -> Self {
        let current_url = gloo_utils::window().location().href().unwrap_or_default();
        let is_freenet = current_url.contains("freenet") || current_url.contains("127.0.0.1:5050");
        let backend_url = option_env!("JANAVANI_BACKEND_URL").map(str::to_owned);

        Self {
            backend_url,
            is_freenet_context: is_freenet,
        }
    }

    pub async fn dispatch_draft_workflow(&self, input_text: String) -> Result<DraftResponse, String> {
        let backend_url = self
            .backend_url
            .as_deref()
            .ok_or_else(|| "No conventional backend is configured; local/decentralized capabilities remain available.".to_string())?;

        let client = reqwest::Client::new();
        let payload = ComplaintRequest {
            citizen_raw_input: input_text,
        };

        let response = client
            .post(format!("{backend_url}/agent/draft"))
            .json(&payload)
            .send()
            .await
            .map_err(|e| format!("Network pipeline connection dropped: {e}"))?;

        if response.status().is_success() {
            response
                .json::<DraftResponse>()
                .await
                .map_err(|e| format!("Response format mismatch: {e}"))
        } else {
            Err(format!("Server returned failure status: {}", response.status()))
        }
    }
}
