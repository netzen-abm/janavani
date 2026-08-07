"""
State Registry

Maps conversation states
to workflow handlers.

The Conversation Engine
never contains workflow logic.

It only asks:

"What handler owns this state?"
"""

from conversation.constants import (
    NEW,
    WAITING_FOR_DOCUMENT,
    WAITING_FOR_DISTRICT,
    WAITING_FOR_OFFICE,
    WAITING_FOR_PREVIEW,
    WAITING_FOR_IDENTITY,
    WAITING_FOR_GENERATE,
)

from conversation.steps.issue import handle_issue
from conversation.steps.document import handle_document
from conversation.steps.district import handle_district
from conversation.steps.office import handle_office
from conversation.steps.preview import handle_preview
from conversation.steps.identity import handle_identity
from conversation.steps.generate import handle_generate


STATE_REGISTRY = {

    NEW: handle_issue,

    WAITING_FOR_DOCUMENT: handle_document,

    WAITING_FOR_DISTRICT: handle_district,

    WAITING_FOR_OFFICE: handle_office,

    WAITING_FOR_PREVIEW: handle_preview,

    WAITING_FOR_IDENTITY: handle_identity,

    WAITING_FOR_GENERATE: handle_generate,

}


def get_handler(state):
    """
    Return the registered handler
    for a conversation state.
    """

    return STATE_REGISTRY.get(state)
