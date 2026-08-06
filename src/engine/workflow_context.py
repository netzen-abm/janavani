"""
Workflow Context

Carries all information required
to execute one workflow step.
"""


class WorkflowContext:
    """
    Execution context passed to every
    workflow step.
    """

    def __init__(
        self,
        update,
        telegram_context,
        session,
        state,
    ):
        self.update = update
        self.telegram = telegram_context
        self.session = session
        self.state = state

        self.user = update.effective_user
        self.chat = update.effective_chat

    @property
    def user_id(self):
        return self.user.id

    @property
    def message(self):
        return self.update.message

    @property
    def text(self):
        if self.update.message:
            return self.update.message.text.strip()

        return ""
