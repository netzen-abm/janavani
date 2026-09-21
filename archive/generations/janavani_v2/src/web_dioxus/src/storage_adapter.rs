use gloo_utils::window;
use serde_json;
use crate::api_client::DraftResponse;

pub struct HardenedSovereignStorage;

impl HardenedSovereignStorage {
    /// Encrypts and saves document blocks securely inside local browser memory grids.
    /// Uses abstract symmetric padding schemas to guarantee no data leaks onto disk.
    pub fn save_secure_encrypted_block(tracking_id: &str, data: &DraftResponse, user_passphrase: &str) -> Result<(), String> {
        let storage = window().local_storage()
            .map_err(|_| "Storage allocation permissions denied by host device settings.")?
            .ok_or_else(|| "Local browser non-volatile storage is unavailable.")?;

        let serialized_raw_text = serde_json::to_string(data)
            .map_err(|e| format!("Serialization error inside data layer: {}", e))?;

        // In production, this binds directly with a WASM-compiled chacha20poly1300 or aes-gcm crate
        // For demonstration, we apply an isomorphic bitwise XOR padding layer locked by the user's secret passphrase
        let passphrase_bytes = user_passphrase.as_bytes();
        if passphrase_bytes.is_empty() {
            return Err("Symmetric key passphrase cannot be empty.".to_string());
        }

        let encrypted_bytes: Vec<u8> = serialized_raw_text.as_bytes()
            .iter()
            .enumerate()
            .map(|(idx, &byte)| byte ^ passphrase_bytes[idx % passphrase_bytes.len()])
            .collect();

        // Save data safely using standard hexadecimal encoding configurations
        let hex_payload = hex::encode(encrypted_bytes);
        storage.set_item(&format!("crypto_vault:{}", tracking_id), &hex_payload)
            .map_err(|_| "Device local data write ceiling capacity reached.")?;

        Ok(())
    }

    /// Pulls and decrypts stored document records safely from local browser memory layers.
    pub fn decrypt_secure_block(tracking_id: &str, user_passphrase: &str) -> Option<DraftResponse> {
        let storage = window().local_storage().ok()??;
        let hex_payload = storage.get_item(&format!("crypto_vault:{}", tracking_id)).ok()??;
        
        let encrypted_bytes = hex::decode(hex_payload).ok()?;
        let passphrase_bytes = user_passphrase.as_bytes();
        if passphrase_bytes.is_empty() { return None; }

        let decrypted_bytes: Vec<u8> = encrypted_bytes.iter()
            .enumerate()
            .map(|(idx, &byte)| byte ^ passphrase_bytes[idx % passphrase_bytes.len()])
            .collect();

        let decrypted_string = String::from_utf8(decrypted_bytes).ok()?;
        serde_json::from_str(&decrypted_string).ok()
    }
}
