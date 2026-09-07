from types import SimpleNamespace

from src.capabilities.civic_case import CivicCaseCapability
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def _identity(user_id: int) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=f"tg-session-{user_id}",
            identity_mode=IdentityMode.ANONYMOUS,
            interface="telegram",
            authentication_method=AuthenticationMethod.NONE,
            session_id=str(user_id),
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT"}),
        )
    )


def _create_case(capability: CivicCaseCapability, identity: IdentityContext):
    return capability.create(
        request=SimpleNamespace(
            case_type=CaseType.COMPLAINT,
            subject="Water supply",
            narrative="Water supply has stopped.",
            jurisdiction=None,
            related_organisation_id=None,
            related_office_id="office-1",
            related_official_id=None,
            related_representative_id=None,
            claims=None,
        ),
        identity=identity,
        source_channel="telegram",
    ).case


def test_telegram_preview_data_comes_from_canonical_owned_case():
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    identity = _identity(42)
    case = _create_case(capability, identity)

    owned = capability.get_owned(case.case_id, identity=identity)
    assert owned is not None
    assert owned.subject == "Water supply"
    assert owned.narrative == "Water supply has stopped."
    assert owned.related_office_id == "office-1"


def test_telegram_preview_cannot_read_another_owner_case():
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    owner = _identity(42)
    other = _identity(43)
    case = _create_case(capability, owner)

    assert capability.get_owned(case.case_id, identity=other) is None
