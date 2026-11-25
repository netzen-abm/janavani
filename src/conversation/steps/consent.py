"""Telegram document-preparation consent and final-readiness interaction."""
from __future__ import annotations

import logging
from io import BytesIO
from uuid import uuid4

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED, WAITING_FOR_GENERATE, WAITING_FOR_READY
from conversation.session import get_ephemeral_issue, get_session
from conversation.state import set_state
from conversation.steps.generate import (
    TelegramGenerationDependencies,
    _identity,
    handle_generate,
)
from src.capabilities.authority import AuthorityCapability
from src.capabilities.letter_drafting import LetterDraftRequest

logger = logging.getLogger(__name__)


async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record preparation consent, persist one shared draft and show it for review."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return
    user_id, text = user.id, (message.text or "").strip().lower()
    if text not in {"yes", "y", "no", "n", "1", "2"}:
        await message.reply_text("Please reply YES to continue or NO to cancel.")
        return
    if text in {"no", "n", "2"}:
        set_state(user_id, COMPLETED)
        await message.reply_text("Consent was not given. No draft was prepared or sent.")
        return

    session = get_session(user_id)
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if not isinstance(dependencies, TelegramGenerationDependencies):
        await message.reply_text("Document preparation is temporarily unavailable.")
        return
    case_id = str(session.get("case_id") or session.get("complaint_id") or "")
    office = session.get("office") or {}
    office_id = office.get("office_id") or office.get("id")
    if not case_id or not office_id:
        await message.reply_text("A canonical Case and verified authority are required before consent.")
        return
    if str(office_id) == "manual":
        await message.reply_text(
            "Your Case is saved for tracking, but the manually entered office is not verified. "
            "Choose a verified authority before preparing a document."
        )
        return

    authority: AuthorityCapability | None = context.application.bot_data.get("authority_capability")
    try:
        if authority is None or dependencies.letter_drafting_capability is None:
            raise LookupError("Required capability is unavailable")
        authority.require_verified_destination(str(office_id))
        identity = _identity(user_id, links=dependencies.identity_link_repository)
        issue = get_ephemeral_issue(user_id)
        if not issue:
            raise ValueError("Transient issue content expired")
        category = str(session.get("category") or "Citizen civic issue")
        dependencies.case_capability.hydrate_transient_content(
            case_id, identity=identity, subject=category, narrative=issue
        )
        dependencies.consent_capability.record_document_preparation_consent(
            case_id, scope=f"office:{office_id}", identity=identity,
            action_id=f"telegram-document-preparation:{case_id}:{update.update_id}",
        )
        document_id = str(session.get("document_id") or f"doc-{uuid4().hex}")
        session["document_id"] = document_id
        drafted = dependencies.letter_drafting_capability.create_draft(
            case_id,
            LetterDraftRequest(subject=category, issue=issue, document_type="Civic complaint"),
            identity=identity,
            document_id=document_id,
        )
        current = dependencies.case_capability.get_owned(case_id, identity=identity)
        if current is None:
            raise LookupError("Case not found")
        status = getattr(current.status, "value", current.status)
        if status == "draft":
            dependencies.case_capability.start_review(case_id, identity=identity)
        elif status != "review":
            raise ValueError("Case is not in a reviewable state")
    except (LookupError, PermissionError, ValueError) as exc:
        logger.info("telegram_consent_rejected error_type=%s", type(exc).__name__)
        await message.reply_text(
            "Consent or draft preparation could not be completed. Confirm the verified authority "
            "and that your issue has not expired; restart if needed."
        )
        return
    except Exception as exc:
        logger.warning("telegram_consent_failed error_type=%s", type(exc).__name__)
        await message.reply_text("Document preparation is temporarily unavailable.")
        return

    set_state(user_id, WAITING_FOR_READY)
    document = drafted.document
    preview = f"Subject: {document.subject}\n\n{document.body}"
    if len(preview) > 20_000:
        preview = preview[:20_000] + "\n\n[Preview truncated. Review the complete document in Janavani before approval.]"
    await message.reply_document(
        document=InputFile(BytesIO(preview.encode("utf-8")), filename="janavani-draft-for-review.txt"),
        caption="Preparation consent is recorded. This is a draft for review only; the Case is not ready and nothing has been sent.",
    )
    await message.reply_text(
        "Read the attached draft. Reply READY to approve this exact saved version for download, "
        "or NO to stop. You must send the document yourself."
    )


async def handle_ready_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve only the persisted, citizen-reviewed draft before artifact generation."""
    message, user = update.effective_message, update.effective_user
    if message is None or user is None:
        return
    text = (message.text or "").strip().lower()
    if text in {"no", "n", "2"}:
        set_state(user.id, COMPLETED)
        await message.reply_text("No final approval was given. The Case remains unsubmitted; no document was sent.")
        return
    if text not in {"ready", "yes", "y", "1"}:
        await message.reply_text("Reply READY to approve the reviewed draft, or NO to stop.")
        return

    session = get_session(user.id)
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if not isinstance(dependencies, TelegramGenerationDependencies):
        await message.reply_text("Final document preparation is temporarily unavailable.")
        return
    case_id = str(session.get("case_id") or session.get("complaint_id") or "")
    try:
        identity = _identity(user.id, links=dependencies.identity_link_repository)
        case = dependencies.case_capability.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        status = getattr(case.status, "value", case.status)
        if status == "review":
            dependencies.case_capability.approve(case_id, identity=identity)
        elif status != "ready":
            raise ValueError("Case is not awaiting final review approval")
    except (LookupError, PermissionError, ValueError) as exc:
        logger.info("telegram_ready_rejected error_type=%s", type(exc).__name__)
        await message.reply_text("The Case could not be marked ready. Reopen the draft and confirm its review state.")
        return
    except Exception as exc:
        logger.warning("telegram_ready_failed error_type=%s", type(exc).__name__)
        await message.reply_text("Final approval is temporarily unavailable.")
        return

    set_state(user.id, WAITING_FOR_GENERATE)
    await message.reply_text("Final review recorded. Generating the approved version for download; nothing will be transmitted.")
    await handle_generate(update, context)
