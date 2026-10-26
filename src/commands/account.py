"""Explicit Telegram sign-up for citizens who want persistent Case tracking."""
from __future__ import annotations

from uuid import uuid4

from telegram import Update
from telegram.ext import ContextTypes

from src.adapters.telegram.identity import identity_for_telegram_user
from src.identity.linking import IdentityLinkRequest, IdentityLinkingService


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create/check a citizen identity only after an explicit private-chat command."""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if message is None or user is None or chat is None:
        return
    if chat.type != "private":
        await message.reply_text(
            "For privacy, account registration is available only in a private chat "
            "with Janavani. You can continue generating anonymous drafts without an account."
        )
        return

    composition = context.application.bot_data.get("surface_case_composition")
    if composition is None:
        await message.reply_text(
            "Persistent account registration is unavailable in this deployment. "
            "Anonymous draft generation remains available; no account was created."
        )
        return

    provider_composition = getattr(composition, "provider_composition", None)
    if (
        provider_composition is None
        or provider_composition.provider_for("external_identity_links") != "postgres"
    ):
        await message.reply_text(
            "Secure account tracking needs the shared PostgreSQL identity store, "
            "which is not configured here. No account was created. You can still "
            "generate and download anonymous drafts."
        )
        return

    repository = getattr(composition, "identity_link_repository", None)
    if repository is None:
        await message.reply_text(
            "The identity store is unavailable. No account was created; please try later."
        )
        return

    subject = str(user.id)
    try:
        existing = repository.find("telegram", subject)
        if existing is not None:
            identity_for_telegram_user(user.id, links=repository)
            await message.reply_text(
                "Your Janavani Telegram account is already active. You can describe "
                "a problem to prepare a draft, or use /cases and /check to track Cases "
                "belonging to this account."
            )
            return

        request = IdentityLinkRequest(
            principal_id="janavani:citizen:" + uuid4().hex,
            provider="telegram",
            subject=subject,
            authentication_method="telegram_bot_update",
        )
        IdentityLinkingService(repository).link_verified(request, verified=True)
        identity_for_telegram_user(user.id, links=repository)
    except (PermissionError, LookupError, ValueError, RuntimeError):
        await message.reply_text(
            "Janavani could not verify or create your account. No additional Case "
            "permissions were granted. Try again later or continue anonymously."
        )
        return

    await message.reply_text(
        "✅ Your Janavani account is ready for optional Case tracking through this "
        "Telegram account. Your Telegram ID is not your public citizen ID, and Janavani "
        "does not receive your Telegram password. You can still choose anonymous drafts "
        "on the WebApp. Account creation does not submit any complaint or RTI.\n\n"
        "Use /privacy to review data handling. Do not send Aadhaar numbers, passwords, "
        "bank details, or unnecessary sensitive information.\n\n"
        "Available next steps: describe an issue, /cases, /check CASE_ID, or /cancel."
    )
