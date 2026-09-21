use dioxus::prelude::*;

#[component]
pub fn JanavaniDocumentEditor(tracking_id: String, initial_text: String, doc_type: String) -> Element {
    let mut current_text = use_signal(|| initial_text.clone());
    let mut edit_status_banner = use_signal(|| "".to_string());
    let mut is_saving = use_signal(|| false);

    let submit_manual_corrections = move |_| {
        let edited_text = current_text.read().clone();
        let original = initial_text.clone();
        let token = tracking_id.clone();
        let scope = doc_type.clone();

        cx.spawn(async move {
            is_saving.set(true);
            let client = reqwest::Client::new();
            let url = "https://janavani.internal";
            
            let payload = serde_json::json!({
                "tracking_token_id": token,
                "original_ai_output_text": original,
                "user_modified_output_text": edited_text,
                "document_scope_type": scope
            });

            match client.post(url)
                .header("X-Janavani-Interface-Token", "web-v2-token")
                .json(&payload)
                .send()
                .await 
            {
                Ok(res) => {
                    if res.status().is_success() {
                        edit_status_banner.set("✔ Layout updated successfully. Janavani learned from your edit anonymously.".to_string());
                    } else {
                        edit_status_banner.set("⚠️ Submission rejected by verification layer.".to_string());
                    }
                },
                Err(_) => edit_status_banner.set("⚠️ Connection error: Backend server unreachable.".to_string()),
            }
            is_saving.set(false);
        });
    };

    rsx! {
        section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 1.5rem;",
            h3 { "📝 Review & Correct Generated Legal Draft" }
            p { style: "font-size: 0.85rem; color: #555;", "Review the document text layout below. You can make manual corrections on screen before downloading. Your edits help train Janavani anonymously." }
            
            textarea {
                rows: "12",
                style: "font-family: monospace; font-size: 0.9rem; line-height: 1.5; padding: 1rem;",
                value: "{current_text}",
                oninput: move |evt| current_text.set(evt.value().clone())
            }
            
            div { class: "grid",
                button { 
                    class: "button primary", 
                    disabled: *is_saving.read(),
                    onclick: submit_manual_corrections, 
                    "Save Corrections & Train System" 
                }
            }

            if !edit_status_banner.read().is_empty() {
                p { style: "font-size: 0.88rem; font-weight: bold; color: #c4732a; margin-top: 1rem;", "{edit_status_banner}" }
            }
        }
    }
}
