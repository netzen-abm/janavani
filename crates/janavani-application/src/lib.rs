//! Provider-neutral application boundary for Janavani.
//!
//! This crate intentionally contains use-case contracts, not HTTP, Telegram,
//! database, AI, or UI implementations. Surface adapters should depend on
//! these contracts and the canonical `janavani-core` domain model.

pub mod cases;

pub use cases::{CaseQuery, CaseUseCases};
