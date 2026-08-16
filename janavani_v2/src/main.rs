#![allow(non_snake_case)]
use dioxus::prelude::*;

mod capability;
mod legal_core;
mod legislative;
mod accountability;
mod whistleblower;
mod protocols;
mod sos;
mod tests;

#[derive(Clone, Debug, Default)]
pub struct AppState {
    pub is_low_resource: bool,
    pub use_local_slm: bool,
    pub opt_in_nostr: bool,
    pub opt_in_nym: bool,
    pub opt_in_reticulum: bool,
    pub opt_in_blockchain: bool,
    pub selected_target: String,
    pub current_gps: String,
}

fn main() {
    # [cfg(not(target_arch = "wasm32"))]
    dioxus::desktop::launch(App);
    # [cfg(target_arch = "wasm32")]
    dioxus::web::launch(App);
}

#[component]
pub fn App() -> Element {
    let mut state = use_signal(|| AppState {
        current_gps: "13.0324, 77.5642".to_string(), // Baseline spatial telemetry location
        ..Default::default()
    });

    let mut log_output = use_signal(|| "System initialized. Web3/4/5/6 modular frameworks verified.".to_string());

    // Run hardware analysis hooks immediately upon runtime entry
    use_hook(move || {
        let mut mutable_state = state.write();
        capability::DeviceEvaluator::optimize_platform_settings(&mut mutable_state);
    });

    let trigger_panic_action = move |danger: &str| {
        let msg = sos::EmergencySOSEngine::trigger_immediate_security_wipe(danger, &state.read().current_gps);
        log_output.set(msg);
    };

    rsx! {
        link { rel: "stylesheet", href: "https://jsdelivr.net" }
        main { class: "container", style: "margin-top: 2rem; max-width: 900px;",
            
            // --- MAIN IDENTITY PANEL HEADER ---
            header { style: "text-align: center; margin-bottom: 2rem;",
                h1 { "🇮🇳 JANAVANI V2: SOVEREIGN CITIZEN PLATFORM" }
                p { I { "Preamble-Driven Collective Oversight & Security Engine Matrix" } }
                div { style: "font-size: 0.8rem; color: gray;", 
                    if state.read().is_low_resource { "⚠️ Low Resource Profile Active: Server Inference Mode" } else { "⚡ High Performance Profile Active: Client WASM Engine Enabled" }
                }
            }

            // --- ALL-CIRCUMSTANCE EMERGENCY SOS PORTAL ---
            section { class: "card", style: "background: #ffe6e6; border: 1px solid #ff9999; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;",
                h4 { style: "color: #cc0000; margin-bottom: 1rem;", "🚨 All-Circumstance Instant SOS System" }
                div { class: "grid",
                    button { style: "background: #cc0000; border:none;", onclick: move |_| trigger_panic_action("Late Night Unsafe Location / Followed"), "Late Night Danger" }
                    button { style: "background: #d97706; border:none;", onclick: move |_| trigger_panic_action("Network Blackout / Direct Physical Threat"), "Network Offline Danger" }
                    button { style: "background: #4b5563; border:none;", onclick: move |_| trigger_panic_action("Administrative Intimidation / Coercion"), "Official Harassment" }
                }
            }

            // --- DYNAMIC PROTOCOL INTERFACE MODULAR TOGGLES ---
            section { class: "card", style: "background: #f1f3f5; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;",
                h4 { "🔌 Sovereignty Protocol Overlays (Opt-In / Opt-Out)" }
                div { class: "grid",
                    label { input { type: "checkbox", checked: state.read().opt_in_nostr, onchange: move |e| state.write().opt_in_nostr = e.value() == "true" }, " Web3 Identity (Nostr)" }
                    label { input { type: "checkbox", checked: state.read().opt_in_nym, onchange: move |e| state.write().opt_in_nym = e.value() == "true" }, " Metadata Obscurity (Nym)" }
                    label { input { type: "checkbox", checked: state.read().opt_in_reticulum, onchange: move |e| state.write().opt_in_reticulum = e.value() == "true" }, " Offline Mesh (Reticulum)" }
                    label { input { type: "checkbox", checked: state.read().opt_in_blockchain, onchange: move |e| state.write().opt_in_blockchain = e.value() == "true" }, " Immutable Trust Ledger" }
                }
            }

            // --- CITIZEN VIGILANCE ACCOUNTABILITY PORTAL ---
            section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem;",
                h3 { "📊 Universal Civic Performance Accountability Ledger" }
                p { "Rate and audit performance metrics for IAS/IPS, MPs/MLAs, local public authorities, schools, or infrastructure sanitization." }
                
                div { class: "grid",
                    select { onchange: move |e| state.write().selected_target = e.value().clone(),
                        option { value: "IAS", "All IAS / IPS / IFS Administrative Hierarchy" }
                        option { value: "MP_MLA", "Members of Parliament (MPs) & Assemblies (MLAs)" }
                        option { value: "LSGD", "Local Self-Government Departments (LSGDs)" }
                        option { value: "INFRA", "Public Services (Hospitals, Schools, Cleanliness)" }
                    }
                    input { type: "text", placeholder: "Target Name, Office Code, or Scheme Title..." }
                }
                button { "Commit Accountability Rating Token" }
            }

            // --- SYSTEM CONSOLE OUTPUT ---
            footer { style: "margin-top: 2rem; background: #222; color: #00ff00; padding: 1rem; border-radius: 4px; font-family: monospace; font-size: 0.85rem;",
                p { "{log_output}" }
            }
        }
    }
}
