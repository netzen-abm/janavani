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
