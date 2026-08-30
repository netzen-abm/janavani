from telegram import Update
from telegram.ext import ContextTypes

from capabilities.authority_directory import DirectoryAuthorityCapability


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for the shared Authority Discovery capability."""
    if len(context.args) < 2:
        await update.message.reply_text(
            """Usage

/search department location

Example

/search ration Kochi
/search village Kannur
/search police Kozhikode"""
        )
        return

    department = context.args[0]
    location = " ".join(context.args[1:])

    capability = DirectoryAuthorityCapability()
    candidates = capability.discover(query=department, jurisdiction=location)

    if not candidates:
        await update.message.reply_text(
            f"No {department} found in {location}."
        )
        return

    lines = [f"Found {len(candidates)} {department}(s) in {location}:\n"]
    for candidate in candidates:
        lines.append(f"ID: {candidate.authority_id}")
        lines.append(f"Name: {candidate.name}")
        if candidate.authority_type:
            lines.append(f"Type: {candidate.authority_type}")
        if candidate.jurisdiction:
            lines.append(f"Jurisdiction: {candidate.jurisdiction}")
        lines.append("---")

    lines.append("Reply with the ID to continue.")
    await update.message.reply_text("\n".join(lines))
