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
