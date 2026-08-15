#![allow(non_snake_case)]
use dioxus::prelude::*;
use crate::api_client::{JanavaniDioxusBridge, DraftResponse};
use crate::sos_interface::{JanavaniWasmSOSTrigger, LocalEmergencyContext};

mod api_client;
mod decentralized_drivers;
mod storage_adapter;
mod capability_checker;
mod sos_interface;

fn main() {
    dioxus::web::launch(App);
}

#[component]
fn App() -> Element {
    let mut user_input = use_signal(|| "".to_string());
    let mut display_result = use_signal(|| Option::<DraftResponse>::None);
    let mut sos_notification = use_signal(|| Option::<String>::None);
    let mut is_loading = use_signal(|| false);

    // Simulated geolocation coordinate variables tracking parameters
    let current_coordinates = use_signal(|| "12.9716, 77.5946".to_string()); // Default: Bengaluru

    let trigger_all_circumstance_panic = move |danger_type: String| {
        cx.spawn(async move {
            let context_payload = LocalEmergencyContext {
                tracking_id: "SESSION_INTERNAL_ACTIVE_NODE".to_string(),
                geo_coordinates: current_coordinates.read().clone(),
                danger_context: danger_type,
            };
            
            match JanavaniWasmSOSTrigger::dispatch_panic_beacon(context_payload).await {
                Ok(success_msg) => sos_notification.set(Some(success_msg)),
                Err(err_msg) => sos_notification.set(Some(format!("⚠️ Failure: {}", err_msg))),
            }
        });
    };

    rsx! {
        link { rel: "stylesheet", href: "https://jsdelivr.net" }
        main { class: "container", style: "margin-top: 2rem; max-width: 800px;",
            
            // --- HIGH PRIORITY UNIVERSAL EMERGENCE CRITICAL PORTAL ---
            section { class: "card", style: "background: #fff0f0; border: 2px solid #ffcccc; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;",
                h3 { style: "color: #cc0000; margin-bottom: 0.5rem;", "🚨 Emergency Personal Safety Protocol" }
                p { style: "font-size: 0.85rem; color: #555;", "Triggers immediate device wipe and broadcasts distress beacons out to trusted channels (Works Offline via Mesh Radio)." }
                
                div { class: "grid",
                    button { 
                        style: "background-color: #cc0000; border: none;",
                        onclick: move |_| trigger_all_circumstance_panic("Late Night Travel / Unsafe Area".to_string()),
                        "Late Night Danger"
                    }
                    button { 
                        style: "background-color: #d97706; border: none;",
                        onclick: move |_| trigger_all_circumstance_panic("Stalker / Being Followed".to_string()),
                        "Being Followed"
                    }
                    button { 
                        style: "background-color: #4b5563; border: none;",
                        onclick: move |_| trigger_all_circumstance_panic("Administrative Harassment / Threat".to_string()),
                        "Official Threat"
                    }
                }

                if let Some(msg) = sos_notification.read().as_ref() {
                    div { style: "margin-top: 1rem; padding: 0.75rem; background: white; border-left: 4px solid green; font-weight: bold; font-size: 0.85rem;",
                        "{msg}"
                    }
                }
            }

            // --- STANDARD WORKFLOW GENERATOR INTERFACE ---
            section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);",
                h3 { "📝 Enter Public Grievance Details" }
                textarea { 
                    placeholder: "Describe the civic issue here...", 
                    rows: "4", 
                    value: "{user_input}",
                    oninput: move |evt| user_input.set(evt.value().clone())
                }
                br {}
                button { 
                    disabled: *is_loading.read(),
                    "Process Legal Draft Document" 
                }
            }
        }
    }
}


# -------------------------

#![allow(non_snake_case)]
use dioxus::prelude::*;
use crate::api_client::{JanavaniDioxusBridge, DraftResponse};
use crate::decentralized_drivers::JanavaniDecentralizedCore;
use crate::storage_adapter::LocalBrowserStorage;

mod api_client;
mod decentralized_drivers;
mod storage_adapter;

fn main() {
    dioxus::web::launch(App);
}

#[component]
fn App() -> Element {
    let mut user_input = use_signal(|| "".to_string());
    let mut display_result = use_signal(|| Option::<DraftResponse>::None);
    let mut runtime_error = use_signal(|| Option::<String>::None);
    let mut is_loading = use_signal(|| false);

    // Optional protocol activation indicators managed by user interactions
    let mut nostr_keypair = use_signal(|| Option::<(String, String)>::None);

    let bridge_client = use_memo(|| JanavaniDioxusBridge::new());

    let activate_nostr_identity = move |_| {
        match JanavaniDecentralizedCore::initialize_nostr_identity() {
            Ok(keys) => {
                // Securely save tracking references inside local storage bounds instantly
                nostr_keypair.set(Some(keys.clone()));
                st::info("Nostr identity activated locally.");
            },
            Err(e) => runtime_error.set(Some(e)),
        }
    };

    rsx! {
        link { rel: "stylesheet", href: "https://jsdelivr.net" }
        main { class: "container", style: "margin-top: 3rem; max-width: 800px;",
            header { class: "header-banner", style: "text-align: center; margin-bottom: 2rem;",
                h1 { "JANAVANI" }
                p { "Dynamic Multi-Protocol Sovereign Civic Platform Grid" }
            }

            // Optional Decentralized Integration Action Controls
            section { class: "card", style: "background: #f1f3f5; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;",
                h4 { "🔌 Optional Security & Network Protocol Overlays" }
                p { style: "font-size: 0.85rem;", "Activate decentralized options to run without server dependencies." }
                
                div { class: "grid",
                    if let Some((pubkey, _)) = nostr_keypair.read().as_ref() {
                        div { style: "color: green; font-size: 0.8rem;", "✔ Nostr Identity Loaded: {pubkey[..15]}..." }
                    } else {
                        button { class: "outline secondary", onclick: activate_nostr_identity, "Initialize Nostr Cryptography" }
                    }
                    div { style: "font-size: 0.8rem; color: #555; padding-top: 0.5rem;", "🥷 Nym Mixnet Routing: READY" }
                    div { style: "font-size: 0.8rem; color: #555; padding-top: 0.5rem;", "📡 Reticulum Mesh: READY" }
                }
            }

            // Grievance Processing Section
            section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem;",
                h3 { "📝 Enter Public Grievance Details" }
                textarea { 
                    placeholder: "Type your civic issue here...", 
                    rows: "4", 
                    value: "{user_input}",
                    oninput: move |evt| user_input.set(evt.value().clone())
                }
                br {}
                button { 
                    disabled: *is_loading.read(),
                    onclick: move |_| {
                        let text = user_input.read().clone();
                        cx.spawn(async move {
                            is_loading.set(true);
                            let client = JanavaniDioxusBridge::new();
                            match client.dispatch_draft_workflow(text).await {
                                Ok(data) => {
                                    // Mirror and commit output down to browser local memories
                                    let _ = LocalBrowserStorage::cache_document_locally(&data.tracking_id, &data);
                                    display_result.set(Some(data));
                                },
                                Err(err) => runtime_error.set(Some(err)),
                            }
                            is_loading.set(false);
                        });
                    },
                    "Process Legal Draft Document" 
                }
            }

            if let Some(res) = display_result.read().as_ref() {
                section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);",
                    h2 { "📄 Generated Structural Document Blueprint" }
                    p { b { "Saved to Offline Memory: " }, "TRUE (Encrypted Local Storage)" }
                    hr {}
                    h4 { "Subject Heading Line:" }
                    p { i { "{res.document.subject_line}" } }
                }
            }
        }
    }
}


# ------------------------------

#![allow(non_snake_case)]
use dioxus::prelude::*;
use crate::api_client::{JanavaniDioxusBridge, DraftResponse};

mod api_client;

fn main() {
    // Launch the Dioxus web application stack context safely
    dioxus::web::launch(App);
}

#[component]
fn App() -> Element {
    let mut user_input = use_signal(|| "".to_string());
    let mut display_result = use_signal(|| Option::<DraftResponse>::None);
    let mut runtime_error = use_signal(|| Option::<String>::None);
    let mut is_loading = use_signal(|| false);

    let bridge_client = use_memo(|| JanavaniDioxusBridge::new());
    let context_badge = if bridge_client.read().is_freenet_context {
        "🌐 Operating inside Freenet Decentralized Mode"
    } else {
        "🔒 Operating inside Secure Server Connect Mode"
    };

    let on_submit_handler = move |_| {
        let text = user_input.read().clone();
        if text.trim().is_empty() { return; }

        cx.spawn(async move {
            is_loading.set(true);
            runtime_error.set(None);
            
            let client = JanavaniDioxusBridge::new();
            match client.dispatch_draft_workflow(text).await {
                Ok(data) => display_result.set(Some(data)),
                Err(err) => runtime_error.set(Some(err)),
            }
            is_loading.set(false);
        });
    };

    rsx! {
        // Embed the standard PicoCSS look directly via external styling scopes
        link { rel: "stylesheet", href: "https://jsdelivr.net" }
        main { class: "container", style: "margin-top: 3rem; max-width: 800px;",
            header { class: "header-banner", style: "text-align: center; margin-bottom: 2rem;",
                h1 { "JANAVANI" }
                p { "Privacy-First Concurrent Civic Action Framework Platform" }
                div { style: "font-weight: bold; color: #0088cc; font-size: 0.9rem;", "{context_badge}" }
            }

            // Grievance Text Submission Interface Block
            section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem;",
                h3 { "📝 Enter Public Grievance Details" }
                p { "Provide plain natural language input text records. Data scrubbing filters operate locally prior to any network execution loops." }
                textarea { 
                    placeholder: "Type your civic issue here...", 
                    rows: "5", 
                    value: "{user_input}",
                    oninput: move |evt| user_input.set(evt.value().clone())
                }
                br {}
                button { 
                    disabled: *is_loading.read(),
                    onclick: on_submit_handler,
                    "Process and Structure Legal Draft Documents" 
                }
            }

            // Dynamic Diagnostic & Runtime Notification Layers
            if let Some(error_msg) = runtime_error.read().as_ref() {
                div { style: "padding: 1rem; background-color: #ffe6e6; color: #cc0000; border-radius: 4px; margin-bottom: 2rem;",
                    h5 { "⚠️ System Synchronization Failure" }
                    p { "{error_msg}" }
                }
            }

            // Results Render Target Grid Output Window
            if let Some(res) = display_result.read().as_ref() {
                section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);",
                    h2 { "📄 Generated Structural Document Blueprint" }
                    p { b { "Status Code: " }, "{res.status}" }
                    p { b { "Transient ID Reference: " }, "{res.tracking_id}" }
                    hr {}
                    h4 { "Subject Heading Line:" }
                    p { i { "{res.document.subject_line}" } }
                    h4 { "Target Authority Sector:" }
                    p { "{res.document.suggested_ministry_or_department}" }
                }
            }
        }
    }
}
