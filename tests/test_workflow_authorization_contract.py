import pytest

from src.authorization.capabilities import DOCUMENT_GENERATE, PUBLIC_CAPABILITIES
from src.authorization.endpoint import AuthorizationDenied
from src.authorization.policy import AuthorizationPolicy
from src.authorization.workflow_guard import authorize_workflow_state


def test_generate_state_is_not_public():
    assert DOCUMENT_GENERATE not in PUBLIC_CAPABILITIES


def test_unknown_workflow_state_has_no_implicit_capability():
    # Unmapped states remain routing-only and cannot acquire authority from state names.
    authorize_workflow_state(123, "WAITING_FOR_ISSUE")


def test_generate_state_is_denied_by_default():
    from src.identity.context import anonymous_context
    from src.authorization.endpoint import authorize_capability

    with pytest.raises(AuthorizationDenied):
        authorize_capability(
            anonymous_context("telegram-session:123", interface="telegram"),
            DOCUMENT_GENERATE,
            policy=AuthorizationPolicy(),
        )
