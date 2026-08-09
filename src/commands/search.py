from telegram import Update
from telegram.ext import ContextTypes

from services.search_directory import search_office


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ------------------------------------
    # Validate Input
    # ------------------------------------

    if len(context.args) < 2:

        await update.message.reply_text(
            """
Usage

/search department location

Example

/search ration Kochi

/search village Kannur

/search police Kozhikode
"""
        )

        return

    # ------------------------------------
    # Read Arguments
    # ------------------------------------

    department = context.args[0]

    location = " ".join(context.args[1:])

    # ------------------------------------
    # Search Office
    # ------------------------------------

    result = search_office(
        department,
        location,
    )

    # ------------------------------------
    # Reply
    # ------------------------------------

    await update.message.reply_text(result)
