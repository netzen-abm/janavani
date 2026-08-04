from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
🇮🇳 Welcome to Janavani

Citizen Governance Platform

Available Commands

/start
/search
/rate
/complaint

Or simply type your problem.

Examples

Broken Road

Water Pipe Leakage

Ration Card Delay

Aadhaar not updated
"""

    await update.message.reply_text(message)
