#![allow(non_snake_case)]

use dioxus::prelude::*;

mod api_client;
mod capability_checker;
mod decentralized_drivers;
mod sos_interface;

use api_client::{CaseDocument, JanavaniDioxusBridge};
use sos_interface::{JanavaniWasmSOSTrigger, LocalEmergencyContext};

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    let mut user_input = use_signal(String::new);
    let mut case_id = use_signal(|| Option::<String>::None);
    let mut case_result = use_signal(|| Option::<CaseDocument>::None);
    let mut runtime_error = use_signal(|| Option::<String>::None);
    let mut sos_notification = use_signal(|| Option::<String>::None);
    let mut is_loading = use_signal(|| false);

    let on_create_case = move |_| {
        let text = user_input.read().trim().to_string();
        if text.is_empty() || *is_loading.read() {
            return;
        }

        is_loading.set(true);
        runtime_error.set(None);

        spawn(async move {
            let client = JanavaniDioxusBridge::new();
            match client.create_case("Civic issue".to_string(), text).await {
                Ok(created) => {
                    case_id.set(Some(created.case_id.clone()));
                    match client.get_case(&created.case_id).await {
                        Ok(case) => case_result.set(Some(case)),
                        Err(err) => runtime_error.set(Some(err)),
                    }
                }
                Err(err) => runtime_error.set(Some(err)),
            }
            is_loading.set(false);
        });
    };

    let on_refresh_case = move |_| {
        let Some(id) = case_id.read().clone() else { return; };
        runtime_error.set(None);
        spawn(async move {
            let client = JanavaniDioxusBridge::new();
            match client.get_case(&id).await {
                Ok(case) => case_result.set(Some(case)),
                Err(err) => runtime_error.set(Some(err)),
            }
        });
    };

    let mut on_sos = move |danger_type: String| {
        sos_notification.set(None);
        spawn(async move {
            let context = LocalEmergencyContext {
                tracking_id: "SESSION_INTERNAL_ACTIVE_NODE".to_string(),
                geo_coordinates: "local-only".to_string(),
                danger_context: danger_type,
            };
            match JanavaniWasmSOSTrigger::dispatch_panic_beacon(context).await {
                Ok(message) => sos_notification.set(Some(message)),
                Err(error) => sos_notification.set(Some(format!(
                    "Emergency capability unavailable: {error}"
                ))),
            }
        });
    };

    rsx! {
        main {
            class: "container",
            style: "margin: 2rem auto; max-width: 900px; padding: 1rem;",
            header {
                style: "text-align: center; margin-bottom: 2rem;",
                h1 { "JANAVANI" }
                p { "The Infrastructure of Citizen Voice" }
                p { style: "font-size: 0.85rem;", "WebApp — shared Civic Case capability" }
            }
            section {
                style: "padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #ddd; border-radius: 8px;",
                h2 { "Civic action" }
                p { "Describe your issue. Janavani creates a canonical case that can be continued across supported access surfaces." }
                textarea {
                    placeholder: "Describe your civic issue...",
                    rows: "6",
                    value: "{user_input}",
                    oninput: move |event| user_input.set(event.value().clone()),
                }
                button {
                    disabled: *is_loading.read(),
                    onclick: on_create_case,
                    if *is_loading.read() { "Creating case…" } else { "Create civic case" }
                }
            }
            if let Some(error) = runtime_error.read().as_ref() {
                section {
                    style: "padding: 1rem; margin-bottom: 1.5rem; border: 1px solid #d66; border-radius: 8px;",
                    h3 { "Civic service unavailable" }
                    p { "{error}" }
                    p { "No browser-side identity secret is embedded. The production WebApp must obtain a server-issued authenticated session/assertion before case operations." }
                }
            }
            if let Some(result) = case_result.read().as_ref() {
                section {
                    style: "padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #aaa; border-radius: 8px;",
                    h2 { "Case workspace" }
                    p { b { "Case: " } "{result.case_id}" }
                    p { b { "Status: " } "{result.status}" }
                    h3 { "Subject" }
                    p { "{result.subject}" }
                    h3 { "Issue" }
                    p { "{result.narrative}" }
                    p { "Evidence references: {result.evidence_refs.len()}" }
                    p { "Document references: {result.document_refs.len()}" }
                    p { "Consent references: {result.consent_refs.len()}" }
                    button { onclick: on_refresh_case, "Refresh case" }
                }
            }
            section {
                style: "padding: 1.25rem; border: 1px solid #ecc; border-radius: 8px;",
                h2 { "Emergency capability" }
                p { "Emergency handling is independent from the ordinary civic case workflow." }
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
