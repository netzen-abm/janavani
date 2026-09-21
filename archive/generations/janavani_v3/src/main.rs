#![allow(non_snake_case)]
use dioxus::prelude::*;
use crate::auto_transport::{InvisibleNetworkMiddleware, ActiveTransportRoute};
use crate::privacy_audit::{SovereignDeviceAuditor, PrivacyAuditReport};

mod auto_transport;
mod capability;
mod legal_shield;
mod privacy_audit;

#[derive(Clone, Debug, Default)]
pub struct AppState {
    pub is_low_resource: bool,
    pub use_local_slm: bool,
    pub dynamic_route: Option<ActiveTransportRoute>,
    pub selected_authority_tier: String,
    pub trace_output_log: String,
}

fn main() {
    # [cfg(not(target_arch = "wasm32"))]
    dioxus::desktop::launch(App);
    # [cfg(target_arch = "wasm32")]
    dioxus::web::launch(App);
}

#[component]
pub fn App() -> Element {
    let mut state = use_signal(|| AppState::default());
    let mut audit_report = use_signal(|| Option::<PrivacyAuditReport>::None);
    let mut issue_input = use_signal(|| "".to_string());

    // Execute on-entry hardware capability checks safely
    use_hook(move || {
        let mut mutable_state = state.write();
        crate::capability::DeviceEvaluator::optimize_platform_settings(&mut mutable_state);
    });

    let run_confidential_forensic_scan = move |_| {
        let report = SovereignDeviceAuditor::run_self_audit_diagnostics();
        audit_report.set(Some(report));
        state.write().trace_output_log = "Local forensic audit complete. Zero server logging logs emitted.".to_string();
    };

    let compile_document_stack_trigger = move |_| {
        let text = issue_input.read().clone();
        if text.trim().is_empty() { return; }

        cx.spawn(async move {
            let target_url = "https://janavani.internal";
            let payload = serde_json::json!({ "citizen_text_input": text }).to_string();
            
            // Execute the Invisible Middleware Routing Algorithm behind the scenes
            match InvisibleNetworkMiddleware::auto_route_payload(target_url, &payload).await {
                Ok((route, body)) => {
                    state.write().dynamic_route = Some(route);
                    state.write().trace_output_log = format!("Success. Route selected: {:?}. Response: {}", route, body);
                },
                Err(err_msg) => state.write().trace_output_log = format!("Routing Exception: {}", err_msg),
            }
        });
    };

    rsx! {
        link { rel: "stylesheet", href: "https://jsdelivr.net" }
        main { class: "container", style: "margin-top: 2rem; max-width: 850px;",
            
            header { style: "text-align: center; margin-bottom: 2.5rem;",
                h1 { "🇮🇳 JANAVANI V3: THE CITIZEN OPERATING SYSTEM" }
                p { i { "Sovereign Citizen Infrastructure — Panchayat to Centre Integration [source 1]" } }
                div { style: "font-size: 0.8rem; color: #7f8c8d; font-weight: bold;",
                    if state.read().is_low_resource { "⚙ PROFILE: Low-Resource Client Mode Active (Server-Assisted Inference)" } else { "⚡ PROFILE: High-Resource Client Mode Active (WASM Engine Enabled)" }
                }
            }

            // --- SECTION 1: CONFIDENTIAL FORENSIC AUDIT CHANNEL ---
            section { class: "card", style: "background: #fdfefe; border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);",
                h4 { "🛡️ Confidential Privacy & Compromise Self-Audit" }
                p { style: "font-size: 0.85rem; color: #555;", "Scan your local runtime environment for tracking nodes, proxy intercepts, or network modifications. Zero bits of diagnostic data leave your device." }
                button { class: "outline secondary", onclick: run_confidential_forensic_scan, "Run Local Environment Audit Scan" }
                
                if let Some(audit) = audit_report.read().as_ref() {
                    div { style: "margin-top: 1rem; padding: 1rem; background: #fafbfc; border-left: 4px solid #c4732a; font-size: 0.88rem;",
                        h6 { "Scan Results & Action Guidelines:" }
                        ul {
                            for step in &audit.remediation_steps {
                                li { "{step}" }
                            }
                        }
                    }
                }
            }

            // --- SECTION 2: CITIZEN VIGILANCE ACCOUNTABILITY PORTAL [source 1] ---
            section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); margin-bottom: 2rem;",
                h3 { "📝 Submit Civic Grievance or Policy Objection [source 1]" }
                p { style: "font-size: 0.88rem; color: #555;", "State your issue or copy a newly introduced bill text layout. The Invisible Middleware handles network selection automatically [source 1]." }
                
                div { class: "grid",
                    select { onchange: move |e| state.write().selected_authority_tier = e.value().clone(),
                        option { value: "IAS", "All IAS / IPS / Public Officers Tier [source 1]" }
                        option { value: "LEGISLATURE", "Constituency MPs / MLAs Tracker [source 1]" }
                        option { value: "LSGD", "Gram Panchayat / Municipal Corporations [source 1]" }
                    }
                    input { type: "text", placeholder: "Enter Officer Code, Target District Name, or Bill ID... [source 1]" }
                }
                
                textarea {
                    placeholder: "Type your grievance statements here...",
                    rows: "4",
                    value: "{issue_input}",
                    oninput: move |evt| issue_input.set(evt.value().clone())
                }
                br {}
                button { class: "button primary", onclick: compile_document_stack_trigger, "Compile Legal Escalation Document Stack [source 1]" }
            }

            // --- CONSOLE DIAGNOSTIC FEEDBACK FOOTER ---
            footer { style: "background: #1a1a2e; color: #00ff00; padding: 1rem; border-radius: 6px; font-family: monospace; font-size: 0.85rem; box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);",
                p { b { "System Telemetry Log Matrix:" } }
                p { "{state.read().trace_output_log}" }
            }
        }
    }
}
