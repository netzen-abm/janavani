from conversation.steps import *

WORKFLOWS = {

    "Complaint": [

        ASK_ISSUE,

        ASK_DOCUMENT,

        ASK_DISTRICT,

        ASK_OFFICE,

        ASK_LANGUAGE,

        ASK_PHOTO,

        PREVIEW,

        GENERATE,

        FINISHED,
    ],

    "RTI": [

        ASK_ISSUE,

        ASK_DOCUMENT,

        ASK_DISTRICT,

        ASK_LANGUAGE,

        PREVIEW,

        GENERATE,

        FINISHED,
    ],

}
