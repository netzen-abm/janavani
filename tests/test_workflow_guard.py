import pytest

from src.authorization.workflow_guard import authorize_workflow_state


def test_protected_workflow_state_is_denied_without_capability():
    with pytest.raises(PermissionError):
        authorize_workflow_state(123, "WAITING_FOR_GENERATE")


def test_unprotected_workflow_state_has_no_required_capability():
    authorize_workflow_state(123, "WAITING_FOR_ISSUE")
