"""
Conversation Workflow

Defines the order of every conversation step.
"""

from conversation.steps import *

WORKFLOW = {

    START: DOCUMENT,

    DOCUMENT: DISTRICT,

    DISTRICT: OFFICE,

    OFFICE: CITIZEN_NAME,

    CITIZEN_NAME: CITIZEN_ADDRESS,

    CITIZEN_ADDRESS: CITIZEN_PHONE,

    CITIZEN_PHONE: CITIZEN_EMAIL,

    CITIZEN_EMAIL: GENERATE_DOCUMENT,

    GENERATE_DOCUMENT: FINISHED,

}
