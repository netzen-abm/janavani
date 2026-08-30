"""Shared authorization policy for Agentic AI tool use."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str | None = None


class AgentToolPolicy:
    """Fail-closed tool policy; consequential actions require confirmation."""

    READ_ONLY_TOOLS = frozenset({"search_public_sources", "read_public_source", "draft_document", "explain"})
    CONSEQUENT_TOOLS = frozenset({"submit_external", "send_message", "publish_publicly", "delete_remote"})

    def authorize(self, tool: str, allowed_tools: frozenset[str], *, user_confirmed: bool = False) -> ToolDecision:
        if tool not in allowed_tools:
            return ToolDecision(False, False, "tool_not_in_user_scope")
        if tool in self.CONSEQUENT_TOOLS:
            if not user_confirmed:
                return ToolDecision(False, True, "explicit_confirmation_required")
            return ToolDecision(True, True)
        if tool in self.READ_ONLY_TOOLS:
            return ToolDecision(True, False)
        return ToolDecision(False, False, "unknown_tool_denied")
