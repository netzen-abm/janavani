use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct CaseCreateRequest {
    pub case_type: String,
    pub subject: String,
    pub narrative: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct CaseResponse {
    pub case_id: String,
    pub status: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct CaseDocument {
    pub case_id: String,
    pub case_type: String,
    pub subject: String,
    pub narrative: String,
    pub status: String,
    pub evidence_refs: Vec<String>,
    pub document_refs: Vec<String>,
    pub consent_refs: Vec<String>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct JanavaniDioxusBridge {
    pub backend_url: Option<String>,
}

impl JanavaniDioxusBridge {
    pub fn new() -> Self {
        Self {
            backend_url: option_env!("JANAVANI_BACKEND_URL").map(str::to_owned),
        }
    }

    pub async fn create_case(&self, subject: String, narrative: String) -> Result<CaseResponse, String> {
        let backend_url = self.backend_url.as_deref().ok_or_else(|| {
            "No Janavani backend is configured for this WebApp environment.".to_string()
        })?;
        let payload = CaseCreateRequest {
            case_type: "complaint".to_string(),
            subject,
            narrative,
        };
        let response = Client::new()
            .post(format!("{backend_url}/civic/cases"))
            .json(&payload)
            .send()
            .await
            .map_err(|e| format!("Case service connection failed: {e}"))?;
        if !response.status().is_success() {
            return Err(format!("Case service returned failure status: {}", response.status()));
        }
        response.json::<CaseResponse>().await.map_err(|e| format!("Case response format mismatch: {e}"))
    }

    pub async fn get_case(&self, case_id: &str) -> Result<CaseDocument, String> {
        let backend_url = self.backend_url.as_deref().ok_or_else(|| {
            "No Janavani backend is configured for this WebApp environment.".to_string()
        })?;
        let response = Client::new()
            .get(format!("{backend_url}/civic/cases/{case_id}"))
            .send()
            .await
            .map_err(|e| format!("Case service connection failed: {e}"))?;
        if !response.status().is_success() {
            return Err(format!("Case service returned failure status: {}", response.status()));
        }
        response.json::<CaseDocument>().await.map_err(|e| format!("Case response format mismatch: {e}"))
    }
}
