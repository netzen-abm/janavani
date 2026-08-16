use crate::main::AppState;

pub struct DeviceEvaluator;

impl DeviceEvaluator {
    pub fn optimize_platform_settings(state: &mut AppState) {
        // Enforces localized UI profiles depending on device resources
        # [cfg(target_arch = "wasm32")]
        {
            let nav = gloo_utils::window().navigator();
            let cores = nav.hardware_concurrency() as u32;
            if cores < 4 {
                state.is_low_resource = true;
                state.use_local_slm = false; // Defer execution to server-side local containers
            }
        }
        # [cfg(not(target_arch = "wasm32"))]
        {
            state.is_low_resource = false; // Mobile native can utilize thread pools directly
        }
    }
}
