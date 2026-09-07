from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_IDENTITY
from src.capabilities.civic_case import CivicCaseCapability
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


def _identity(user_id: int) -> IdentityContext:
    """Map the Telegram session to the same opaque Case owner used at creation."""
    return IdentityContext(
        principal=Principal(
            principal_id=f"tg-session-{user_id}",
            identity_mode=IdentityMode.ANONYMOUS,
            interface="telegram",
            authentication_method=AuthenticationMethod.NONE,
            session_id=str(user_id),
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT"}),
        )
    )


def build_case_preview(*, capability: CivicCaseCapability, case_id: str, user_id: int) -> str:
    """Build preview text from the canonical owned Case without legacy reconstruction."""
    case = capability.get_owned(case_id, identity=_identity(user_id))
    if case is None:
        raise LookupError("Case not found")

    authority = case.related_office_id or "Not selected"
    return (
        f"Issue:\n{case.narrative}\n\n"
        f"Category:\n{case.subject}\n\n"
        f"Authority reference:\n{authority}"
    )


async def handle_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show the canonical Case preview before identity selection."""
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    session = get_session(user_id)
    case_id = str(session.get("case_id") or "")

    try:
        capability = CivicCaseCapability(context.bot_data["case_repository"])
        preview_text = build_case_preview(
            capability=capability,
            case_id=case_id,
            user_id=user_id,
        )
    except (LookupError, ValueError) as exc:
        print("❌ PREVIEW ERROR:", exc)
        await update.message.reply_text(
            "⚠️ Your canonical case could not be loaded. Please restart the civic issue flow."
        )
        return

    await update.message.reply_text(
        f"📄 Complaint Preview\n\n"
        f"{preview_text}\n\n"
        "---\n\n"
        "Choose Identity Mode:\n\n"
        "1️⃣ Anonymous\n"
        "2️⃣ Name Only\n"
        "3️⃣ Address Only\n"
        "4️⃣ Full Details\n\n"
        "Reply with 1, 2, 3, or 4."
    )

    set_state(user_id, WAITING_FOR_IDENTITY)
