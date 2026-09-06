//! Canonical Janavani domain kernel entry point.

mod consent;

pub use consent::{Consent, ConsentGrantType, ConsentStatus};

include!("civic_case.rs");
