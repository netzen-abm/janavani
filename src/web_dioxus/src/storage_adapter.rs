use crate::api_client::DraftResponse;
use gloo_utils::window;
use serde_json;

pub struct LocalBrowserStorage;

impl LocalBrowserStorage {
    /// Stores Janavani document data locally for offline continuity.
    pub fn cache_document_locally(
        tracking_id: &str,
        data: &DraftResponse,
    ) -> Result<(), String> {
        let storage = window()
            .local_storage()
            .map_err(|_| "Failed to access browser storage permissions.".to_string())?
            .ok_or_else(|| "Local storage is unavailable.".to_string())?;
        let serialized = serde_json::to_string(data)
            .map_err(|e| format!("Serialization error: {e}"))?;
        let key = format!("local_doc:{tracking_id}");

        storage
            .set_item(&key, &serialized)
            .map_err(|_| "Browser storage limit reached.".to_string())
    }

    /// Retrieves a Janavani document from local browser storage.
    pub fn retrieve_document_locally(tracking_id: &str) -> Option<DraftResponse> {
        let storage = window().local_storage().ok()??;
        let key = format!("local_doc:{tracking_id}");
        let raw_item = storage.get_item(&key).ok()??;
        serde_json::from_str(&raw_item).ok()
    }
}
