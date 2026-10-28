from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
🇮🇳 Welcome to Janavani

Citizen Governance Platform

PRIVACY NOTE
This is a Telegram bot chat, not an end-to-end encrypted Secret Chat or a
local-only Janavani session. Messages needed to operate the bot are processed by
Telegram and Janavani's bot service. Please do not send identity documents, highly
sensitive personal details, or original evidence in this chat. Share only what is
necessary, and review Janavani's privacy information before continuing.

I can help you:

✅ Generate Complaint

✅ Generate Grievance

✅ Generate Grievance Petition

✅ Generate RTI Application

✅ Generate Representation Letter

------------------------------------

You can either use commands

/start

/search

/rate

/complaint

/ai_draft — interactive complaint, grievance, RTI, representation or petition drafting

Or simply type your problem.

Example:

• My road has been broken for 3 months

• Water pipe leakage near my house

• My ration card is delayed

• Pension not received

• Aadhar update pending

------------------------------------

Janavani will guide you step by step.
"""

    await update.message.reply_text(message)
