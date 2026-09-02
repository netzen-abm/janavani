use gloo_utils::window;
use js_sys::Reflect;
use wasm_bindgen::JsValue;

#[derive(Debug, Clone, Copy)]
pub enum DocumentGenerationStrategy {
    LocalWasmCompilation,
    ServerSideDeferredFallback,
}

pub struct DeviceCapabilityChecker;

impl DeviceCapabilityChecker {
    /// Inspects browser capabilities to select a safe processing path.
    pub fn assess_execution_strategy() -> DocumentGenerationStrategy {
        let browser_window = window();
        let navigator = browser_window.navigator();
        let cpu_cores = navigator.hardware_concurrency();
        let memory_api_available = browser_window
            .performance()
            .and_then(|performance| {
                Reflect::get(&performance, &JsValue::from_str("memory")).ok()
            })
            .is_some_and(|value| !value.is_undefined() && !value.is_null());

        if cpu_cores < 4.0 || !memory_api_available {
            DocumentGenerationStrategy::ServerSideDeferredFallback
        } else {
            DocumentGenerationStrategy::LocalWasmCompilation
        }
    }
}
