#[cfg(test)]
mod tests {
    use crate::legal_shield::LegalShieldCopilot;

    #[test]
    fn test_legal_shield_three_part_generation_integrity() {
        let stack = LegalShieldCopilot::compile_enforcement_stack(
            "The District Collector",
            "Revenue Department",
            "Encroachment of local common water bodies.",
            "Tamil Nadu"
        );

        // Verify all three structural documents exist and enforce statutory parameters
        assert!(stack.primary_representation.contains("ARTICLE 21"));
        assert!(stack.calendar_locked_rti.contains("RIGHT TO INFORMATION ACT"));
        assert!(stack.disciplinary_memorandum.contains("BHARATIYA SAKSHYA ADHINIYAM"));
    }
}
