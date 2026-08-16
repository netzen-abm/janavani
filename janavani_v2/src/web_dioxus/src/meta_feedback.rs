use dioxus::prelude::*;

#[component]
pub fn PlatformFeedbackPanel() -> Element {
    let mut scope_tag = use_signal(|| "UI".to_string());
    let mut feedback_text = use_signal(|| "".to_string());
    let mut status_banner = use_signal(|| "".to_string());

    let post_suggestion = move |_| {
        let text = feedback_text.read().clone();
        let tag = scope_tag.read().clone();
        if text.trim().is_empty() { return; }

        cx.spawn(async move {
            let client = reqwest::Client::new();
            let url = "https://janavani.internal";
            
            let payload = serde_json::json!({
                "feature_scope_tag": tag,
                "user_suggestion_body": text
            });

            match client.post(url).json(&payload).send().await {
                Ok(res) => {
                    if res.status().is_success() {
                        status_banner.set("✔ Thank you! Your anonymous suggestion has been logged directly into our improvement loop.".to_string());
                        feedback_text.set("".to_string());
                    } else {
                        status_banner.set("⚠️ Submission rejected by gateway.".to_string());
                    }
                },
                Err(_) => status_banner.set("⚠️ Connection error: Platform offline.".to_string()),
            }
        });
    };

    rsx! {
        section { class: "card", style: "background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 2rem;",
            h3 { "💡 Suggest Platform Upgrades & Features" }
            p { style: "font-size: 0.85rem; color: #555;", "Help improve Janavani. Submit your anonymous feedback or bug reports directly into our core development cycle." }
            
            div { class: "grid",
                select { onchange: move |e| scope_tag.set(e.value().clone()),
                    option { value: "UI", "User Interface & Experience (UI/UX)" }
                    option { value: "AI-Drafting", "AI Drafting & Document Core" }
                    option { value: "SOS-Mesh", "SOS & Reticulum Mesh Systems" }
                    option { value: "Privacy-Audit", "Privacy & Security Audits" }
                }
            }
            textarea {
                placeholder: "Type your feature ideas, suggestions, or critique here...",
                rows: "3",
                value: "{feedback_text}",
                oninput: move |evt| feedback_text.set(evt.value().clone())
            }
            button { class: "button secondary", onclick: post_suggestion, "Submit Improvement Ticket" }

            if !status_banner.read().is_empty() {
                p { style: "font-size: 0.85rem; font-weight: bold; color: green; margin-top: 1rem;", "{status_banner}" }
            }
        }
    }
}
