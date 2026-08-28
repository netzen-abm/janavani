from src.storage.canonical_persistence import memory_persistence, supabase_persistence


class Client:
    def table(self, name: str):
        raise AssertionError(f"database call should not happen during composition: {name}")


def test_memory_composition_builds_workflow() -> None:
    persistence = memory_persistence()
    case = persistence.workflow.create_case("Test civic issue")
    assert case.issue == "Test civic issue"
    assert persistence.workflow.cases.get(case.id) is case
    assert persistence.relationships is None


def test_supabase_composition_builds_all_resource_boundaries() -> None:
    persistence = supabase_persistence(Client())
    assert persistence.workflow.cases.__class__.__name__ == "SupabaseCaseRepository"
    assert persistence.workflow.evidence.__class__.__name__ == "SupabaseEvidenceRepository"
    assert persistence.workflow.authorities.__class__.__name__ == "SupabaseAuthorityRepository"
    assert persistence.workflow.submissions.__class__.__name__ == "SupabaseSubmissionRepository"
    assert persistence.documents.__class__.__name__ == "SupabaseDocumentRepository"
    assert persistence.relationships.__class__.__name__ == "CanonicalRelationshipRepository"
