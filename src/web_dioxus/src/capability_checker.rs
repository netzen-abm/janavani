use web_sys::window;
use gloo_utils::window as gloo_window;

#[derive(Debug, Clone, Copy)]
pub enum DocumentGenerationStrategy {
    LocalWasmCompilation,
    ServerSideDeferredFallback,
}

pub struct DeviceCapabilityChecker;

impl DeviceCapabilityChecker {
    /// Inspects local hardware performance metrics to select an optimal processing path.
    pub fn assess_execution_strategy() -> DocumentGenerationStrategy {
        let nav = gloo_window().navigator();
        
        // 1. Core Count Evaluation (Detect low-tier mobile processors)
        let CPU_cores = nav.hardware_concurrency() as u32;
        
        // 2. Memory Footprint Assessment (Using the window performance memory web-sys API hooks)
        let is_low_memory_device = if let Ok(Some(perf)) = gloo_window().performance() {
            // Check if the device reports constrained execution states
            let raw_js_perf = js_sys::Reflect::get(&perf, &wasm_bindgen::JsValue::from_str("memory")).is_ok();
            CPU_cores < 4 || !raw_js_perf
        } else {
            true
        };

        // 3. Select strategy based on device capabilities
        if CPU_cores < 4 || is_low_memory_device {
            // Safe fallback route for low-powered mobile devices
            DocumentGenerationStrategy::ServerSideDeferredFallback
        } else {
            // High-speed generation route for powerful desktop or high-end mobile devices
            DocumentGenerationStrategy::LocalWasmCompilation
        }
    }
}
