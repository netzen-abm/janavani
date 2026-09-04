use janavani_core::CaseStatus;

/// Channel-neutral query for a citizen case.
///
/// The application layer does not prescribe storage, transport, or UI. A
/// surface may populate only the fields it can legitimately provide.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CaseQuery {
    pub case_id: String,
}

/// Read-side application contract shared by Web, Telegram, and future
/// surfaces. Mutation commands will be added only when their domain
/// invariants are represented by `janavani-core`.
pub trait CaseUseCases {
    type Error;

    fn get_case(&self, query: CaseQuery) -> Result<CaseStatus, Self::Error>;
}
