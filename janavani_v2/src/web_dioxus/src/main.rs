// Add these layout elements inside your App component configuration block
use crate::privacy_audit::{ZeroCollectionAuditEngine, AuditReport};

mod privacy_audit;

// Inside the App render loop layout definition:
let mut local_audit_state = use_signal(|| Option::<AuditReport>::None);

let run_confidential_scan = move |_| {
    let report = ZeroCollectionAuditEngine::execute_local_privacy_scan();
    local_audit_state.set(Some(report));
};

// Insert this section right above your footer rendering block inside main.rs
rsx! {
    section { class: "card", style: "background: #f8f9fa; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;",
        h4 { "🔒 Optional Privacy & Device Security Audit" }
        p { style: "font-size: 0.85rem; color: #666;", "Scan your local browser runtime for unauthorized network modifications or proxy redirects. This diagnostic runs completely on your device; no system data is sent to our servers." }
        
        button { class: "outline primary", onclick: run_confidential_scan, "Run Local Environment Audit Scan" }

        if let Some(audit) = local_audit_state.read().as_ref() {
            div { style: "margin-top: 1rem; padding: 1rem; background: white; border-radius: 4px; border-left: 4px solid #4a90e2;",
                h5 { "Scan Diagnostics & Resolution Steps:" }
                ul {
                    for step in &audit.resolution_steps {
                        li { style: "font-size: 0.88rem; margin-bottom: 0.25rem;", "{step}" }
                    }
                }
            }
        }
    }
}

// Add these layout elements inside your App component configuration block
use crate::privacy_audit::{SovereignDeviceAuditor, PrivacyAuditReport};

mod privacy_audit;

// Inside the App render loop layout definition:
let mut dynamic_audit_results = use_signal(|| Option::<PrivacyAuditReport>::None);

let run_confidential_device_audit = move |_| {
    let report = SovereignDeviceAuditor::run_self_audit_diagnostics();
    dynamic_audit_results.set(Some(report));
};

// Insert this panel section right above the system console output block in main.rs
rsx! {
    section { class: "card", style: "background: #f8f9fa; border: 1px solid #e2e8f0; padding: 2rem; border-radius: 8px; margin-bottom: 2rem;",
        h3 { "🛡️ Confidential Privacy & Device Compromise Audit" }
        p { style: "font-size: 0.88rem; color: #555;", 
            "Scan your local application runtime for unauthorized proxy routing or device tracking markers. "
            "This check runs entirely inside your device's browser memory workspace—zero bits of system diagnostic metrics leave this terminal."
        }
        
        button { class: "outline secondary", onclick: run_confidential_device_audit, "Execute Local Privacy Audit Scan" }

        if let Some(audit) = dynamic_audit_results.read().as_ref() {
            div { style: "margin-top: 1.5rem; padding: 1.25rem; background: white; border-radius: 6px; border-left: 4px solid #c4732a; box-shadow: 0 2px 4px rgba(0,0,0,0.02);",
                h5 { "Scan Diagnostics & Action Guidelines:" }
                ul {
                    for step in &audit.remediation_steps {
                        li { style: "font-size: 0.9rem; margin-bottom: 0.5rem; color: #2a1f14;", "{step}" }
                    }
                }
            }
        }
    }
}

// Inject the component directly near your footer inside main.rs
use crate::meta_feedback::PlatformFeedbackPanel;

mod meta_feedback;

// Inside the master rsx! render macro loop:
rsx! {
    // Existing blocks...
    PlatformFeedbackPanel {}
}
