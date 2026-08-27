//! Client execution-strategy capability.
//!
//! This module only reports observable client constraints. It does not make
//! civic, legal, security, or authority determinations.

use gloo_utils::window;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DocumentGenerationStrategy {
    LocalWasmCompilation,
    ServerSideDeferredFallback,
    Unavailable,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ExecutionObservation {
    pub hardware_concurrency: Option<u32>,
    pub memory_api_exposed: bool,
}

pub struct DeviceCapabilityChecker;

impl DeviceCapabilityChecker {
    /// Collects browser observations without converting them into domain facts.
    pub fn observe_execution_environment() -> ExecutionObservation {
        let navigator = window().navigator();
        let hardware_concurrency = match navigator.hardware_concurrency() {
            value if value > 0 => Some(value as u32),
            _ => None,
        };

        let memory_api_exposed = window()
            .performance()
            .ok()
            .and_then(|performance| {
                js_sys::Reflect::get(
                    &performance,
                    &wasm_bindgen::JsValue::from_str("memory"),
                )
                .ok()
            })
            .is_some();

        ExecutionObservation {
            hardware_concurrency,
            memory_api_exposed,
        }
    }

    /// Selects an execution path from explicit local observations.
    pub fn assess_execution_strategy(
        observation: ExecutionObservation,
    ) -> DocumentGenerationStrategy {
        match observation.hardware_concurrency {
            None => DocumentGenerationStrategy::ServerSideDeferredFallback,
            Some(cores) if cores < 4 => DocumentGenerationStrategy::ServerSideDeferredFallback,
            Some(_) if observation.memory_api_exposed => {
                DocumentGenerationStrategy::LocalWasmCompilation
            }
            Some(_) => DocumentGenerationStrategy::ServerSideDeferredFallback,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unknown_cpu_count_uses_deferred_fallback() {
        let observation = ExecutionObservation {
            hardware_concurrency: None,
            memory_api_exposed: false,
        };
        assert_eq!(
            DeviceCapabilityChecker::assess_execution_strategy(observation),
            DocumentGenerationStrategy::ServerSideDeferredFallback
        );
    }

    #[test]
    fn low_core_device_uses_deferred_fallback() {
        let observation = ExecutionObservation {
            hardware_concurrency: Some(2),
            memory_api_exposed: true,
        };
        assert_eq!(
            DeviceCapabilityChecker::assess_execution_strategy(observation),
            DocumentGenerationStrategy::ServerSideDeferredFallback
        );
    }

    #[test]
    fn capable_device_can_use_local_wasm() {
        let observation = ExecutionObservation {
            hardware_concurrency: Some(8),
            memory_api_exposed: true,
        };
        assert_eq!(
            DeviceCapabilityChecker::assess_execution_strategy(observation),
            DocumentGenerationStrategy::LocalWasmCompilation
        );
    }
}
