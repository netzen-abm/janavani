use gloo_utils::window;
use serde_json;
use crate::api_client::DraftResponse;

pub struct LocalBrowserStorage;

impl LocalBrowserStorage {
    /// Commits generated document summaries to the citizen's browser memory grid.
    /// Guarantees data availability offline without tracking inputs on a remote hosting node.
    pub fn cache_document_locally(tracking_id: &str, data: &DraftResponse) -> Result<(), String> {
        let storage = window().local_storage()
            .map_err(|_| "Failed to access browser storage permissions.")?
            .ok_or_else(|| "Local storage space is deactivated by policy.")?;

        let serialized = serde_json::to_string(data)
            .map_err(|e| format!("Serialization error: {}", e))?;

        storage.set_item(&format!("local_doc:{}", tracking_id), &serialized)
            .map_err(|_| "Browser storage limit reached.")?;

        Ok(())
    }

    /// Pulls saved document records back out from local browser memory layers.
    pub fn retrieve_document_locally(tracking_id: &str) -> Option<DraftResponse> {
        let storage = window().local_storage().ok()??;
        let raw_item = storage.get_item(&format!("local_doc:{}", tracking_id)).ok()??;
        serde_json::from_str(&raw_item).ok()
    }
}
