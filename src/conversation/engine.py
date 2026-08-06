"""
Conversation Engine

Routes every conversation state
to the correct workflow step.
"""

from conversation.state import get_state

from conversation.constants import (
    NEW,
    WAITING_FOR_DOCUMENT,
    WAITING_FOR_DISTRICT,
    WAITING_FOR_OFFICE,
    WAITING_FOR_PREVIEW,
    WAITING_FOR_IDENTITY,
)

from conversation.handler import handle_message

from conversation.steps.issue import handle_issue
from conversation.steps.document import handle_document
from conversation.steps.district import handle_district
from conversation.steps.office import handle_office
from conversation.steps.preview import handle_preview
from conversation.steps.identity import handle_identity


# ======================================================
# Conversation Engine
# ======================================================

async def run_step(update, context):

    user_id = update.effective_user.id

    state = get_state(user_id)

    # ------------------------------------------
    # STEP 1
    # Issue
    # ------------------------------------------

    if state == NEW:

        await handle_issue(update, context)

        return

    # ------------------------------------------
    # STEP 2
    # Document
    # ------------------------------------------

    if state == WAITING_FOR_DOCUMENT:

        await handle_document(update, context)

        return

    # ------------------------------------------
    # STEP 3
    # District
    # ------------------------------------------

    if state == WAITING_FOR_DISTRICT:

        await handle_district(update, context)

        return

    # ------------------------------------------
    # STEP 4
    # Office
    # ------------------------------------------

    if state == WAITING_FOR_OFFICE:

        await handle_office(update, context)

        return

    # ------------------------------------------
    # STEP 5
    # Preview
    # ------------------------------------------

    if state == WAITING_FOR_PREVIEW:

        await handle_preview(update, context)

        return

    # ------------------------------------------
    # STEP 6
    # Identity
    # ------------------------------------------

    if state == WAITING_FOR_IDENTITY:

        await handle_identity(update, context)

        return

    # ------------------------------------------
    # Legacy Handler
    # ------------------------------------------

    await handle_message(update, context)
