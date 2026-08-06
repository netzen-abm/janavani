"""
Issue Workflow Step

Captures the citizen's issue
and moves the workflow to
document selection.
"""

from workflow.base_step import WorkflowStep

from conversation.constants import (
    WAITING_FOR_DOCUMENT,
)

from conversation.state import set_state


class IssueStep(WorkflowStep):

    async def execute(self, ctx):

        ctx.session["issue"] = ctx.text

        set_state(
            ctx.user_id,
            WAITING_FOR_DOCUMENT
        )

        await ctx.message.reply_text(
f"""
✅ Your issue has been recorded.

Issue

{ctx.session["issue"]}

----------------------------------

Select document

1️⃣ Complaint

2️⃣ RTI

Reply with

1

or

2
"""
        )
