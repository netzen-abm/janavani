from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
🇮🇳 Welcome to Janavani

Citizen Governance Platform

I can help you:

✅ Generate Complaint

✅ Generate Grievance

✅ Generate Grievance Petition

✅ Generate RTI Application

✅ Generate Representation Letter

------------------------------------

You can either use commands

/start

/help

/cancel — clear the current workflow and transient in-memory state

/privacy — explain data handling and privacy limits

/search

/rate

/complaint
/check <Case ID> — check a Case you own
/pair <code> — start a pairing attempt; not linked until confirmed

Web citizen workspace: /app is available only on deployments where the workspace is enabled.
When available, drafts stay in your browser until you download or print them.

------------------------------------

Or simply type your problem.

Example:

• My road has been broken for 3 months

• Water pipe leakage near my house

• My ration card is delayed

• Pension not received

• Aadhar update pending

------------------------------------

Janavani will guide you step by step.

Before describing an issue, review /privacy. The current webhook path stores only the
Telegram update ID plus processing/attempt/lease metadata in PostgreSQL, not the message body.
Older payload-bearing queue rows, if any, may remain until the compatibility worker resumes.
There is no independent cleanup job for those legacy rows while that worker is offline.
Until legacy cleanup is verified, share only minimum necessary, non-sensitive details.
A pairing code is not a completed link. Confirm only in an authenticated account-linking screen that reports success; this screen is not yet part of every deployment.
A command being accepted does not mean a complaint was submitted to an authority.
"""
    if update.message:
        await update.message.reply_text(message)
