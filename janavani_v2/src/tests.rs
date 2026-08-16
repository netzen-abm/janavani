#[cfg(test)]
mod tests {
    use crate::legal_core::LegalDraftingEngine;
    use crate::legislative::LegislativeMonitor;
    use crate::protocols::nostr::NostrMeshDriver;

    #[test]
    fn test_constitutional_authority_and_preamble_anchoring() {
        let doc = LegalDraftingEngine::generate_citizen_petition(
            "District Magistrate, Thiruvananthapuram",
            "Broken drainage structures causing continuous health risks.",
            "LSGD_GRIEVANCE",
            2
        );
        
        assert!(doc.preamble_anchor.contains("WE, THE PEOPLE OF INDIA"));
        assert!(doc.constitutional_authority.contains(&"Article 21 (Right to Life and Personal Dignity)".to_string()));
        assert!(doc.statutory_invocation.contains("Bharatiya Sakshya Adhiniyam, 2023"));
    }

    #[test]
    fn test_golden_triangle_bill_audit_rejection() {
        let intrusive_bill_summary = "Requires mandatory continuous background tracking verification data.";
        let audit = LegislativeMonitor::audit_bill("Digital Tracking Act 2026", intrusive_bill_summary);
        
        assert_eq!(audit.golden_triangle_compliance, false);
        assert!(audit.article_21_breach.is_some());
    }

    #[test]
    fn test_nostr_sovereign_identity_generation_bounds() {
        let (pubkey, seckey) = NostrMeshDriver::initialize_sovereign_identity();
        assert!(pubkey.starts_with("npub1"));
        assert!(seckey.starts_with("nsec"));
    }
}
