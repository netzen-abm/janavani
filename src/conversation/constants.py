"""
Conversation States
"""

# --------------------------------------------------
# Initial State
# --------------------------------------------------

NEW = "NEW"

# --------------------------------------------------
# Conversation Steps
# --------------------------------------------------

WAITING_FOR_ISSUE = "WAITING_FOR_ISSUE"
WAITING_FOR_DOCUMENT = "WAITING_FOR_DOCUMENT"
WAITING_FOR_DISTRICT = "WAITING_FOR_DISTRICT"

WAITING_FOR_OFFICE = "WAITING_FOR_OFFICE"
WAITING_FOR_OFFICE_MANUAL = "WAITING_FOR_OFFICE_MANUAL"

WAITING_FOR_PREVIEW = "WAITING_FOR_PREVIEW"
WAITING_FOR_IDENTITY = "WAITING_FOR_IDENTITY"

# 🔥 NEW
WAITING_FOR_NAME = "WAITING_FOR_NAME"
WAITING_FOR_ADDRESS = "WAITING_FOR_ADDRESS"
WAITING_FOR_FORMAT = "WAITING_FOR_FORMAT"

WAITING_FOR_GENERATE = "WAITING_FOR_GENERATE"

# --------------------------------------------------
# Finished
# --------------------------------------------------

COMPLETED = "COMPLETED"
