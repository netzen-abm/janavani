from src.authorization.policy import AuthorizationPolicy
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def test_anonymous_capability_can_be_explicitly_allowed():
    context = IdentityContext(Principal("anon-1"))
    decision = AuthorizationPolicy(frozenset({"public.search"})).authorize(context, "public.search")
    assert decision.allowed is True


def test_capability_is_denied_by_default():
    context = IdentityContext(Principal("anon-1"))
    decision = AuthorizationPolicy().authorize(context, "citizen.submit")
    assert decision.allowed is False


def test_granted_capability_is_allowed():
    principal = Principal("user-1", capabilities=frozenset({"citizen.submit"}))
    context = IdentityContext(principal)
    decision = AuthorizationPolicy().authorize(context, "citizen.submit")
    assert decision.allowed is True
