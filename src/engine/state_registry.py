from conversation.constants import *

# --------------------------------------------------
# IMPORT HANDLERS (ALL IN ONE PLACE)
# --------------------------------------------------

from conversation.steps.issue import handle_issue
from conversation.steps.document import handle_document
from conversation.steps.district import handle_district
from conversation.steps.office import handle_office
from conversation.steps.office_manual import handle_office_manual
from conversation.steps.preview import handle_preview
from conversation.steps.identity import handle_identity
from conversation.steps.format import handle_format
from conversation.steps.generate import handle_generate
from conversation.steps.name import handle_name
from conversation.steps.address import handle_address
from conversation.steps.office_fallback import handle_office_fallback


# --------------------------------------------------
# SINGLE SOURCE OF TRUTH
# --------------------------------------------------

STATE_HANDLERS = {

    # 🔹 Core Flow
    WAITING_FOR_ISSUE: handle_issue,
    WAITING_FOR_DOCUMENT: handle_document,
    WAITING_FOR_DISTRICT: handle_district,

    # 🔹 Office Selection
    WAITING_FOR_OFFICE: handle_office,
    WAITING_FOR_OFFICE_MANUAL: handle_office_manual,
    WAITING_FOR_OFFICE_FALLBACK: handle_office_fallback,

    # 🔹 Preview + Identity
    WAITING_FOR_PREVIEW: handle_preview,
    WAITING_FOR_IDENTITY: handle_identity,

    # 🔹 Identity Details
    WAITING_FOR_NAME: handle_name,
    WAITING_FOR_ADDRESS: handle_address,

    # 🔹 Format + Generate
    WAITING_FOR_FORMAT: handle_format,
    WAITING_FOR_GENERATE: handle_generate,
}


# --------------------------------------------------
# ROUTER FUNCTION
# --------------------------------------------------

def get_handler(state):
    return STATE_HANDLERS.get(state)