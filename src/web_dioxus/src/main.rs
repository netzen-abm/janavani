#![allow(non_snake_case)]

use dioxus::prelude::*;

mod api_client;
mod capability_checker;
mod decentralized_drivers;
mod sos_interface;
mod storage_adapter;

use api_client::{DraftResponse, JanavaniDioxusBridge};
use sos_interface::{JanavaniWasmSOSTrigger, LocalEmergencyContext};

fn main() {
    dioxus::web::launch(App);
}

#[component]
fn App() -> Element {
    let mut user_input = use_signal(String::new);
    let mut display_result = use_signal(|| Option::<DraftResponse>::None);
    let mut runtime_error = use_signal(|| Option::<String>::None);
    let mut sos_notification = use_signal(|| Option::<String>::None);
    let mut is_loading = use_signal(|| false);

    let current_coordinates = use_signal(|| "12.9716, 77.5946".to_string());
    let bridge_client = use_memo(JanavaniDioxusBridge::new);

    let on_submit = move |_| {
        let text = user_input.read().trim().to_string();
        if text.is_empty() || *is_loading.read() {
            return;
        }

        is_loading.set(true);
        runtime_error.set(None);

        spawn(async move {
            let client = JanavaniDioxusBridge::new();
            match client.dispatch_draft_workflow(text).await {
                Ok(data) => display_result.set(Some(data)),
                Err(err) => runtime_error.set(Some(err)),
            }
            is_loading.set(false);
        });
    };

    let on_sos = move |danger_type: String| {
        let coordinates = current_coordinates.read().clone();
        sos_notification.set(None);

        spawn(async move {
            let context = LocalEmergencyContext {
                tracking_id: "SESSION_INTERNAL_ACTIVE_NODE".to_string(),
                geo_coordinates: coordinates,
                danger_context: danger_type,
            };

            match JanavaniWasmSOSTrigger::dispatch_panic_beacon(context).await {
                Ok(message) => sos_notification.set(Some(message)),
                Err(error) => sos_notification.set(Some(format!("Emergency capability unavailable: {error}"))),
            }
        });
    };

    let context_badge = if bridge_client.read().is_freenet_context {
        "Decentralized mode detected"
    } else {
        "Standard network mode"
    };

    rsx! {
        main {
            class: "container",
            style: "margin: 2rem auto; max-width: 900px; padding: 1rem;",

            header {
                style: "text-align: center; margin-bottom: 2rem;",
                h1 { "JANAVANI" }
                p { "Independent civic capabilities — App / DApp / Web" }
                p { style: "font-size: 0.85rem;", "{context_badge}" }
            }

            section {
                style: "padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #ddd; border-radius: 8px;",
                h2 { "Capability status" }
                p { "Capabilities are isolated. An unavailable network, AI or decentralized adapter must not block unrelated civic workflows." }
                ul {
                    li { "Civic document workflow: available" }
                    li { "Freenet adapter: optional" }
                    li { "Nostr / mesh adapters: optional" }
                    li { "AI adapters: optional" }
                    li { "Blockchain / wallet: optional" }
                }
            }

            section {
                style: "padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #ddd; border-radius: 8px;",
                h2 { "Civic action" }
                p { "Describe a public-service issue. You retain control over review and submission." }
                textarea {
                    placeholder: "Describe your civic issue...",
                    rows: "6",
                    value: "{user_input}",
                    oninput: move |event| user_input.set(event.value().clone()),
                }
                button {
                    disabled: *is_loading.read(),
                    onclick: on_submit,
                    if *is_loading.read() { "Processing…" } else { "Prepare civic document" }
                }
            }

            if let Some(error) = runtime_error.read().as_ref() {
                section {
                    style: "padding: 1rem; margin-bottom: 1.5rem; border: 1px solid #d66; border-radius: 8px;",
                    h3 { "Civic workflow unavailable" }
                    p { "{error}" }
                    p { "Other independent capabilities remain available." }
                }
            }

            if let Some(result) = display_result.read().as_ref() {
                section {
                    style: "padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #aaa; border-radius: 8px;",
                    h2 { "Document preview" }
                    p { b { "Status: " } "{result.status}" }
                    p { b { "Tracking reference: " } "{result.tracking_id}" }
                    h3 { "Subject" }
                    p { "{result.document.subject_line}" }
                    h3 { "Suggested authority" }
                    p { "{result.document.suggested_ministry_or_department}" }
                    h3 { "Factual points" }
                    for point in result.document.factual_points.iter() {
                        p { "• {point}" }
                    }
                }
            }

            section {
                style: "padding: 1.25rem; border: 1px solid #ecc; border-radius: 8px;",
                h2 { "Emergency capability" }
                p { "Emergency handling is a separate capability and must not be required by ordinary civic workflows." }
                div {
                    button { onclick: move |_| on_sos("Late Night Travel / Unsafe Area".to_string()), "Late night danger" }
                    button { onclick: move |_| on_sos("Stalker / Being Followed".to_string()), "Being followed" }
                    button { onclick: move |_| on_sos("Administrative Harassment / Threat".to_string()), "Official threat" }
                }
                if let Some(message) = sos_notification.read().as_ref() {
                    p { "{message}" }
                }
            }
        }
    }
}
