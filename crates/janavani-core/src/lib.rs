//! Canonical, channel-neutral Janavani domain kernel.
//!
//! This crate starts with the CivicCase lifecycle contract. It intentionally
//! contains no database, Telegram, HTTP, AI, or UI dependencies.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CaseStatus {
    Draft,
    Review,
    Ready,
    Submitting,
    Queued,
    Submitted,
    Acknowledged,
    FollowUp,
    InProgress,
    Responded,
    Resolved,
    Escalated,
    Closed,
    Archived,
}

impl CaseStatus {
    /// Canonical transition predicate. Orthogonal events such as evidence
    /// attachment are intentionally outside this status graph.
    pub fn can_transition(self, target: Self) -> bool {
        use CaseStatus::*;
        match self {
            Draft => matches!(target, Review),
            Review => matches!(target, Review | Ready),
            Ready => matches!(target, Ready | Submitting),
            Submitting => matches!(target, Submitting | Queued | Submitted),
            Queued => matches!(target, Queued | Submitted),
            Submitted => matches!(target, Acknowledged),
            Acknowledged => matches!(target, FollowUp | InProgress | Responded | Escalated),
            FollowUp => matches!(target, FollowUp | Responded | Escalated),
            InProgress => matches!(target, FollowUp | Responded | Escalated),
            Responded => matches!(target, FollowUp | Resolved | Escalated),
            Resolved => matches!(target, Closed),
            Escalated => matches!(target, Responded | Closed),
            Closed => matches!(target, Archived),
            Archived => false,
        }
    }

    pub fn require_transition(self, target: Self) -> Result<(), LifecycleError> {
        if self.can_transition(target) {
            Ok(())
        } else {
            Err(LifecycleError::InvalidTransition {
                from: self,
                to: target,
            })
        }
    }

    pub fn confirmed_delivery(self) -> bool {
        use CaseStatus::*;
        matches!(
            self,
            Acknowledged | FollowUp | InProgress | Responded | Resolved | Escalated | Closed
        )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LifecycleError {
    InvalidTransition { from: CaseStatus, to: CaseStatus },
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_happy_path_is_valid() {
        use CaseStatus::*;
        let path = [
            (Draft, Review),
            (Review, Ready),
            (Ready, Submitting),
            (Submitting, Queued),
            (Queued, Submitted),
            (Submitted, Acknowledged),
            (Acknowledged, InProgress),
            (InProgress, Responded),
            (Responded, Resolved),
            (Resolved, Closed),
            (Closed, Archived),
        ];
        for (from, to) in path {
            assert!(from.can_transition(to), "{from:?} -> {to:?}");
        }
    }

    #[test]
    fn invalid_shortcuts_are_rejected() {
        use CaseStatus::*;
        assert!(!Draft.can_transition(Submitted));
        assert!(!Submitted.can_transition(Resolved));
        assert!(!Acknowledged.can_transition(Closed));
        assert!(!Archived.can_transition(Draft));
    }

    #[test]
    fn acknowledgement_is_delivery_boundary() {
        use CaseStatus::*;
        assert!(!Submitted.confirmed_delivery());
        assert!(Acknowledged.confirmed_delivery());
        assert!(Closed.confirmed_delivery());
    }

    #[test]
    fn serde_uses_contract_values() {
        assert_eq!(
            serde_json::to_string(&CaseStatus::FollowUp).unwrap(),
            "\"follow_up\""
        );
        assert_eq!(
            serde_json::to_string(&CaseStatus::InProgress).unwrap(),
            "\"in_progress\""
        );
    }
}
