"""Security guard for conversation workflow states.

Workflow state is routing data, not authority. Protected capabilities must be
checked at the execution boundary as well as at command entry points.
"""

from src.authorization.capabilities import DOCUMENT_GENERATE, PUBLIC_CAPABILITIES
from src.authorization.endpoint import authorize_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context


STATE_CAPABILITIES = {
    "WAITING_FOR_GENERATE": DOCUMENT_GENERATE,
}


def authorize_workflow_state(user_id: int, state: str, *, interface: str = "telegram") -> None:
    capability = STATE_CAPABILITIES.get(state)
    if capability is None:
        return

    context = anonymous_context(
        f"telegram-session:{user_id}",
        interface=interface,
    )
    policy = AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES)
    authorize_capability(context, capability, policy=policy)
