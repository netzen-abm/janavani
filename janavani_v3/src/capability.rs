use crate::main::AppState;

pub struct DeviceEvaluator;

impl DeviceEvaluator {
    /// Dynamically optimizes processing configurations to ensure low-tier mobile devices don't freeze during local processing.
    pub fn optimize_platform_settings(state: &mut AppState) {
        # [cfg(target_arch = "wasm32")]
        {
            let nav = gloo_utils::window().navigator();
            let processor_cores = nav.hardware_concurrency() as u32;
            
            // Check performance memory allocation layers if exposed by the browser environment
            let is_low_spec = if let Ok(Some(perf)) = gloo_utils::window().performance() {
                let has_mem = js_sys::Reflect::get(&perf, &wasm_bindgen::JsValue::from_str("memory")).is_ok();
                processor_cores < 4 || !has_mem
            } else {
                true
            };

            if is_low_spec {
                state.is_low_resource = true;
                state.use_local_slm = false; // Defer file generation and transcription tasks to isolated server containers
            } else {
                state.is_low_resource = false;
                state.use_local_slm = true;  // Run processing locally within WebAssembly
            }
        }
        # [cfg(not(target_arch = "wasm32"))]
        {
            // Native Android/iOS containers use local binary compilation threads directly
            state.is_low_resource = false;
            state.use_local_slm = true;
        }
    }
}
