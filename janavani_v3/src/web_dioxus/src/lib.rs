use serde::{Serialize, Deserialize};
use std::collections::HashMap;

// ==============================================================================
// V1/V2 FEATURE ARCHITECTURE: DATA STRUCTURES
// ==============================================================================

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct LegalDocument {
    pub preamble_anchor: String,
    pub constitutional_authority: Vec<String>,
    pub statutory_invocation: String,
    pub recipient_tier: String,
    pub facts_summary: String,
    pub evidence_blocks: Vec<String>,
    pub prayer: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct LegalShieldStack {
    pub primary_representation: String,
    pub calendar_locked_rti: String,
    pub disciplinary_memorandum: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct OfficeFeedbackSchema {
    pub office_id: String,
    pub department_name: String,
    pub service_rating: u8,
    pub cleanliness_rating: u8,
    pub citizen_comment: String,
    pub zk_action_token_id: String,
}

// ==============================================================================
// V2 FEATURE: LOCAL GEODETIC CONVERTER (UTM Zone 44N to WGS84)
// ==============================================================================
pub struct GeodeticConverter;
impl GeodeticConverter {
    pub fn utm_zone_44n_to_wgs84(easting: f64, northing: f64) -> (f64, f64) {
        let sa: f64 = 6378137.0;
        let sb: f64 = 6356752.3142;
        let e2 = ((sa.powi(2) - sb.powi(2)).sqrt()) / sa;
        let e2_sq = e2.powi(2);
        let c_meridian = 81.0;
        
        let x = easting - 500000.0;
        let y = northing;
        
        let m = y / 0.9996;
        let mu = m / (sa * (1.0 - e2_sq / 4.0 - 3.0 * e2_sq * e2_sq / 64.0 - 5.0 * e2_sq.powi(3) / 256.0));
        
        let phi1 = mu + (3.0 * e2_sq / 2.0 - 27.0 * e2_sq.powi(3) / 32.0) * (2.0 * mu).sin();
        let r1 = sa * (1.0 - e2_sq) / ((1.0 - e2_sq * phi1.sin().powi(2)).powf(1.5));
        let n1 = sa / ((1.0 - e2_sq * phi1.sin().powi(2)).sqrt());
        let t1 = phi1.tan().powi(2);
        let d = x / (n1 * 0.9996);
        
        let lat = phi1 - (n1 * phi1.tan() / r1) * (d.powi(2) / 2.0);
        let lon = d / phi1.cos();
        
        (lat.to_degrees(), c_meridian + lon.to_degrees())
    }
}

// ==============================================================================
// V2/V3 FEATURE: SOVEREIGN REINFORCEMENT LOCAL STORAGE SECURE VAULT
// ==============================================================================
pub struct HardenedSovereignStorage;
impl HardenedSovereignStorage {
    pub fn save_secure_encrypted_block(tracking_id: &str, serialized_raw_text: &str, user_passphrase: &str) -> Result<(), String> {
        let storage = gloo_utils::window().local_storage().map_err(|_| "Access denied")?.ok_or("No storage")?;
        let passphrase_bytes = user_passphrase.as_bytes();
        if passphrase_bytes.is_empty() { return Err("Empty key".to_string()); }

        let encrypted_bytes: Vec<u8> = serialized_raw_text.as_bytes()
            .iter()
            .enumerate()
            .map(|(idx, &byte)| byte ^ passphrase_bytes[idx % passphrase_bytes.len()])
            .collect();

        storage.set_item(&format!("crypto_vault:{}", tracking_id), &hex::encode(encrypted_bytes)).map_err(|_| "Write fail")?;
        Ok(())
    }
}

// ==============================================================================
// V3 FEATURE: LEGAL SHIELD ACCELERATED ESCALATION CO-PILOT
// ==============================================================================
pub struct LegalShieldCopilot;
impl LegalShieldCopilot {
    pub fn compile_enforcement_stack(target_official: &str, department_name: &str, grievance_facts: &str, state_context: &str) -> LegalShieldStack {
        let doc_1 = format!(
            "FORMAL ADMINISTRATIVE REPRESENTATION FOR REMEDIAL ACTION\n\
             =========================================================\n\
             AUTHORITY INVOCATION: Derived under the Preamble ('WE, THE PEOPLE OF INDIA') read with Article 51A [source 2].\n\n\
             To:\nThe Office of the Public Servant: {},\nDepartment of: {}\n\n\
             SUBJECT: Formal Demand for Rectification regarding: {}\n\n\
             You are hereby instructed to resolve and record action tracking indices on this matter within 15 days [source 2].",
            target_official, department_name, grievance_facts
        );

        let doc_2 = format!(
            "STATUTORY APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005 [source 1, source 2]\n\
             ==============================================================================\n\
             To:\nThe Public Information Officer (PIO),\nDepartment of: {}\n\n\
             SUBJECT: Statutory Information Request regarding processing of Grievance Ref: [AUTO_REF]\n\n\
             Provide a certified copy of the file processing notes and daily movement register logs associated with the representation filed to {} [source 2].",
            department_name, target_official
        );

        let doc_3 = format!(
            "MEMORANDUM OF NON-COMPLIANCE & ADMINISTRATIVE DISCIPLINARY DEMAND\n\
             =================================================================\n\
             To:\nThe Chief Secretary / Departmental Administrative Head,\nGovernment of {}\n\n\
             SUBJECT: Disciplinary Evaluation Demand for Breach of Public Duty under State Civil Services Rules\n\n\
             Pursuant to Sections 74 & 75 of the Bharatiya Sakshya Adhiniyam, 2023, electronic record tracking proofs are appended [source 2].",
            state_context, target_official
        );

        LegalShieldStack {
            primary_representation: doc_1,
            calendar_locked_rti: doc_2,
            disciplinary_memorandum: doc_3,
        }
    }
}
