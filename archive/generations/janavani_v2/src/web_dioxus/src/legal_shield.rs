use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct LegalShieldStack {
    pub primary_representation: String,
    pub calendar_locked_rti: String,
    pub disciplinary_memorandum: String,
}

pub struct LegalShieldCopilot;

impl LegalShieldCopilot {
    /// Compiles a three-part legal escalation stack to enforce bureaucratic accountability.
    pub fn compile_enforcement_stack(
        target_official: &str,
        department_name: &str,
        grievance_facts: &str,
        state_context: &str,
    ) -> LegalShieldStack {
        // DOCUMENT 1: Primary representation addressing the immediate official
        let doc_1 = format!(
            "FORMAL ADMINISTRATIVE REPRESENTATION FOR REMEDIAL ACTION\n\
             =========================================================\n\
             To:\nThe Office of: {},\nDepartment of: {}\n\n\
             SUBJECT: Formal Demand for Rectification regarding: {}\n\n\
             Respected Authority,\n\n\
             This representation is formally submitted under the mandate of Article 21 (Right to Life & Dignity) \
             read with the sovereign status derived from the Preamble. You are hereby requested to inspect, resolve, \
             and record action tracking indices on this matter within 15 days.",
            target_official, department_name, grievance_facts
        );

        // DOCUMENT 2: Automated, calendar-locked RTI query form to trace non-compliance
        let doc_2 = format!(
            "STATUTORY APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005\n\
             ==============================================================================\n\
             To:\nThe Public Information Officer (PIO),\nDepartment of: {}\n\n\
             SUBJECT: Statutory Information Request regarding processing of Grievance Ref: [AUTO_REF]\n\n\
             Provide the following certified records within the mandatory 30-day window:\n\
             1. Provide a certified copy of the file processing notes and daily movement register logs associated with the representation filed to {} on [DATE_0].\n\
             2. Provide the names and designations of the public servants responsible for verifying compliance during this period.",
            department_name, target_official
        );

        // DOCUMENT 3: Disciplinary Escalation Memorandum addressed straight to the state Chief Secretary
        let doc_3 = format!(
            "MEMORANDUM OF NON-COMPLIANCE & ADMINISTRATIVE DISCIPLINARY DEMAND\n\
             =================================================================\n\
             To:\nThe Chief Secretary / Departmental Administrative Head,\nGovernment of {}\n\n\
             SUBJECT: Disciplinary Evaluation Demand for Breach of Public Duty under State Civil Services Rules\n\n\
             Respected Sir/Madam,\n\n\
             This memorandum is filed invoking Article 14 and Article 51A. Despite formal representations and statutory reminders, \
             the office of {} has failed to execute its public duties. Pursuant to Sections 74 & 75 of the Bharatiya Sakshya Adhiniyam, 2023, \
             electronic record tracking proofs are appended. Please initiate immediate administrative actions against the non-compliant officers.",
            state_context, target_official
        );

        LegalShieldStack {
            primary_representation: doc_1,
            calendar_locked_rti: doc_2,
            disciplinary_memorandum: doc_3,
        }
    }
}
