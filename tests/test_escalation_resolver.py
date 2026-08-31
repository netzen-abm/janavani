from src.core.capabilities.escalation_resolver import EscalationRoute, SharedEscalationResolver
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus


class Provider:
    def __init__(self, routes):
        self._routes = routes

    def routes_for(self, procedure_id, from_authority_id):
        return self._routes


def authority(status=AuthorityStatus.VERIFIED):
    return AuthorityCandidate("next", "Next Authority", "department", "IN-KL", "verified route", ("official-source",), status)


def test_only_verified_routes_and_authorities_are_returned():
    routes = (
        EscalationRoute("r1", "procedure-1", "current", authority(), "verified escalation" , True),
        EscalationRoute("r2", "procedure-1", "current", authority(), "unverified route", False),
        EscalationRoute("r3", "procedure-1", "current", authority(AuthorityStatus.CANDIDATE), "unverified destination", True),
    )
    result = SharedEscalationResolver(Provider(routes)).resolve(procedure_id="procedure-1", from_authority_id="current")
    assert [item.route_id for item in result] == ["r1"]
    assert result[0].requires_user_confirmation is True


def test_missing_inputs_fail():
    resolver = SharedEscalationResolver(Provider(()))
    try:
        resolver.resolve(procedure_id="", from_authority_id="current")
        assert False
    except ValueError:
        pass
