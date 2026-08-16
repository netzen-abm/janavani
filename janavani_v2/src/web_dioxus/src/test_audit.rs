#[cfg(test)]
mod tests {
    use crate::privacy_audit::ZeroCollectionAuditEngine;

    #[test]
    fn test_local_privacy_audit_execution_profile() {
        // Assert that the client-side diagnostic loop executes reliably without crashing
        let report = ZeroCollectionAuditEngine::execute_local_privacy_scan();
        
        // Ensure the engine correctly structures and compiles diagnostic findings
        assert!(!report.resolution_steps.is_empty());
        assert!(
            report.resolution_steps[0].contains("Clean") || 
            report.resolution_steps[0].contains("Warning") ||
            report.resolution_steps[0].contains("Critical")
        );
    }
}

#[cfg(test)]
mod tests {
    use crate::privacy_audit::SovereignDeviceAuditor;

    #[test]
    fn test_local_privacy_audit_execution_profile() {
        // Assert that the client-side diagnostic loop executes reliably without crashing
        let report = SovereignDeviceAuditor::run_self_audit_diagnostics();
        
        // Ensure the engine correctly structures and compiles diagnostic findings
        assert!(!report.remediation_steps.is_empty());
        assert!(
            report.remediation_steps[0].contains("Clean") || 
            report.remediation_steps[0].contains("Warning") ||
            report.remediation_steps[0].contains("Critical") ||
            report.remediation_steps[0].contains("NOTICE")
        );
    }
}
