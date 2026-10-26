from telegram import Update
from telegram.ext import ContextTypes

VOLUNTEER_URL = "https://github.com/netzen-abm/janavani"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the citizen-first welcome and primary actions."""
    del context
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "🇮🇳 Welcome to Janavani\n"
        "The Infrastructure of Citizen Voice\n\n"
        "Prepare a complaint or an RTI request for existing public records.\n\n"
        "• Send one issue in your own words, or use /complaint.\n"
        "• /search ration Kochi — search the current authority directory.\n"
        "• /rate <office_id> <1-5> <issue> — share service feedback.\n"
        "• /help — commands and next steps.\n"
        "• /privacy — how your information is handled.\n"
        "• /cancel — clear the current temporary workflow.\n\n"
        "Drafts are for you to review; Janavani does not submit anything automatically.\n"
        "Generated files are currently in English; Malayalam translation is not enabled yet.\n\n"
        "Volunteer in coding, tests, accessibility, language support, or documentation:\n"
        f"{VOLUNTEER_URL}\n"
        "Never post citizen narratives, personal data, API keys, or secrets in public issues."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show concise command guidance instead of repeating the welcome message."""
    del context
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "Janavani help\n\n"
        "Start a draft: send a short description of one civic issue in this private chat, "
        "or use /complaint. No account is needed to generate an anonymous draft.\n\n"
        "/complaint — begin a guided complaint workflow.\n"
        "/search <department> <location> — search the authority directory. A missing match "
        "does not prove that no office exists.\n"
        "/rate <office_id> <1-5> <issue> — share service feedback.\n"
        "/account — opt in to persistent Case tracking where configured.\n"
        "/cases and /check <Case ID> — inspect tracked Cases you own.\n"
        "/pair <code> — start account pairing; confirm only in an authenticated Web session.\n"
        "/privacy — review data handling. /cancel — clear the temporary workflow.\n\n"
        "Generated files are currently in English; Malayalam translation is not enabled yet.\n"
        "Review every fact and placeholder. Nothing is submitted automatically.\n\n"
        "Volunteer in coding, tests, accessibility, Indian-language support, or documentation:\n"
        f"{VOLUNTEER_URL}\n"
        "Never post citizen narratives, personal data, credentials, or API keys in public issues."
    )
