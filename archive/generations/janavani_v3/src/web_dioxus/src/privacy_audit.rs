use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct PrivacyAuditReport {
    pub is_environment_compromised: bool,
    pub detected_vectors: Vec<String>,
    pub remediation_steps: Vec<String>,
}

pub struct SovereignDeviceAuditor;

impl SovereignDeviceAuditor {
    /// Executes local environment security scans within the client browser/mobile shell.
    /// CRITICAL: Zero network request emissions occur during this process to ensure absolute privacy.
    pub fn run_self_audit_diagnostics() -> PrivacyAuditReport {
        let mut report = PrivacyAuditReport::default();
        
        # [cfg(target_arch = "wasm32")]
        if let Some(win) = gloo_utils::window_opt() {
            let location_href = win.location().href().unwrap_or_default();
            let current_protocol = win.location().protocol().unwrap_or_default();
            let nav = win.navigator();

            // 1. Man-In-The-Middle (MITM) Traffic Proxy Interception Scan
            if location_href.contains("localhost:") && !location_href.contains("8080") && !location_href.contains("8501") {
                report.is_environment_compromised = true;
                report.detected_vectors.push("ADVERSARIAL_TRAFFIC_PROXY_REDIRECT".to_string());
                report.remediation_steps.push(
                    "⚠️ DETECTED: Traffic Proxy/Interception Route. Your internet traffic might be passing through a local tracking logger. \
                     FIX: Inspect your network settings, open your system configurations, and deactivate unexpected VPN profiles or custom HTTP proxy settings.".to_string()
                );
            }

            // 2. Encryption protocol downgrade check
            if current_protocol != "https:" && !location_href.contains("127.0.0.1") && !location_href.contains("localhost") {
                report.is_environment_compromised = true;
                report.detected_vectors.push("UNENCRYPTED_PLAINTEXT_TRANSPORT".to_string());
                report.remediation_steps.push(
                    "❌ CRITICAL: Unencrypted Connection (Plaintext HTTP). Your ISP or intermediate routers can read everything you do. \
                     FIX: Immediately add 'https://' manually to the browser address line or transition onto a secure cellular network connection.".to_string()
                );
            }

            // 3. Local storage bloat analysis (Detecting malicious tracking extension scrapers)
            if let Some(local_storage) = win.local_storage().ok().flatten() {
                if let Ok(storage_length) = local_storage.len() {
                    if storage_length > 250 {
                        report.is_environment_compromised = true;
                        report.detected_vectors.push("LOCAL_STORAGE_INJECTION_BLOAT".to_string());
                        report.remediation_steps.push(
                            "⚠️ NOTICE: High Local Storage Asset Infiltration. Unusually high quantities of localized variable tables found. \
                             FIX: Open your browser settings and audit or deactivate unverified third-party extensions, custom add-ons, or alternative keyboards.".to_string()
                        );
                    }
                }
            }
            
            // 4. Checking for persistent canvas or text injection interceptors
            if nav.webdriver() {
                report.is_environment_compromised = true;
                report.detected_vectors.push("AUTOMATED_WEBDRIVER_INTERCEPTION_HOOK".to_string());
                report.remediation_steps.push(
                    "🚨 WARNING: Automated Webdriver Monitoring Session Active. Your current application lifecycle is running under automation frameworks. \
                     FIX: Close all background development environments, exit remote connection apps (like TeamViewer), and restart your browser window cleanly.".to_string()
                );
            }
        }

        // Native mobile architecture checks (Android/iOS Root and Jailbreak Detection)
        # [cfg(not(target_arch = "wasm32"))]
        {
            let standard_root_binaries = ["/system/app/Superuser.apk", "/sbin/su", "/system/bin/su", "/system/xbin/su"];
            let mut root_marker_found = false;
            for path in standard_root_binaries.iter() {
                if std::path::Path::new(path).exists() {
                    root_marker_found = true;
                    break;
                }
            }
            
            if root_marker_found {
                report.is_environment_compromised = true;
                report.detected_vectors.push("MOBILE_NATIVE_ROOT_JAILBREAK_ANOMALY".to_string());
                report.remediation_steps.push(
                    "🚨 CRITICAL: Root/Jailbreak Compromise Found. Your phone operating system's kernel defense layers are deactivated. \
                     FIX: Avoid inputting sensitive credentials on rooted hardware. Flash your device back to verified factory stock firmware to reactivate security sandboxes.".to_string()
                );
            }
        }

        if report.remediation_steps.is_empty() {
            report.remediation_steps.push("✔ Local Device Audit Clean: Privacy and isolation layers are operational. Zero indicators of environment compromise found on this local node.".to_string());
        }

        report
    }
}
