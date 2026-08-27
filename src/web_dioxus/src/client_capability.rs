//! Provider-neutral client capability boundary.
//!
//! UI code should consume capability state and responses through this module
//! rather than embedding domain decisions or provider-specific behavior.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CapabilityState {
    Available,
    Unavailable,
    Degraded,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CapabilityStatus {
    pub capability: &'static str,
    pub state: CapabilityState,
    pub reason: Option<String>,
}

impl CapabilityStatus {
    pub fn available(capability: &'static str) -> Self {
        Self {
            capability,
            state: CapabilityState::Available,
            reason: None,
        }
    }

    pub fn unavailable(capability: &'static str, reason: impl Into<String>) -> Self {
        Self {
            capability,
            state: CapabilityState::Unavailable,
            reason: Some(reason.into()),
        }
    }

    pub fn degraded(capability: &'static str, reason: impl Into<String>) -> Self {
        Self {
            capability,
            state: CapabilityState::Degraded,
            reason: Some(reason.into()),
        }
    }
}

/// A client-side capability adapter exposes availability; it does not decide
/// whether a civic fact, authority, or legal conclusion is true.
pub trait ClientCapabilityAdapter {
    fn status(&self) -> CapabilityStatus;
}

pub struct ConventionalNetworkCapability {
    configured: bool,
}

impl ConventionalNetworkCapability {
    pub fn new(configured: bool) -> Self {
        Self { configured }
    }
}

impl ClientCapabilityAdapter for ConventionalNetworkCapability {
    fn status(&self) -> CapabilityStatus {
        if self.configured {
            CapabilityStatus::available("conventional_network")
        } else {
            CapabilityStatus::unavailable(
                "conventional_network",
                "No conventional backend is configured",
            )
        }
    }
}

pub struct DeviceLocationCapability;

impl ClientCapabilityAdapter for DeviceLocationCapability {
    fn status(&self) -> CapabilityStatus {
        match web_sys::window()
            .and_then(|window| window.navigator().geolocation().ok())
        {
            Some(_) => CapabilityStatus::available("device_location"),
            None => CapabilityStatus::unavailable(
                "device_location",
                "Browser geolocation is unavailable",
            ),
        }
    }
}
