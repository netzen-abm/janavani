//! Canonical, channel-neutral Janavani domain kernel.
//!
//! This crate contains the CivicCase aggregate, event model, and lifecycle
//! contract. It intentionally contains no database, Telegram, HTTP, AI, or UI
//! dependencies.

mod consent;

pub use consent::{Consent, ConsentGrantType, ConsentStatus};

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

pub type JsonObject = BTreeMap<String, Value>;
