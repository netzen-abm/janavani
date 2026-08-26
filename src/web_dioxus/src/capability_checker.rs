use gloo_utils::window as gloo_window;

#[derive(Debug, Clone, Copy)]
pub enum DocumentGenerationStrategy {
    LocalWasmCompilation,
    ServerSideDeferredFallback,
}

pub struct DeviceCapabilityChecker;

impl DeviceCapabilityChecker {
    /// Inspects local hardware metrics and selects a safe processing path.
    pub fn assess_execution_strategy() -> DocumentGenerationStrategy {
        let nav = gloo_window().navigator();
        let cpu_cores = nav.hardware_concurrency() as u32;

        // Performance is optional in browsers. A missing Performance object
        // must degrade to the safer server-side path rather than fail startup.
        let has_performance_memory = gloo_window()
            .performance()
            .map(|perf| {
                js_sys::Reflect::get(
                    &perf,
                    &wasm_bindgen::JsValue::from_str("memory"),
                )
                .is_ok()
            })
            .unwrap_or(false);

        let is_low_memory_device = cpu_cores < 4 || !has_performance_memory;

        if is_low_memory_device {
            DocumentGenerationStrategy::ServerSideDeferredFallback
        } else {
            DocumentGenerationStrategy::LocalWasmCompilation
        }
    }
}
