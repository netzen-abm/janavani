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

✅ Register an optional account with /account to track Cases

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
/account — opt in to persistent Case tracking (requires shared identity storage)
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

Before describing an issue, review /privacy. Webhook updates are encrypted before
they enter Janavani's PostgreSQL inbox and have a maximum 24-hour processing window.
The running worker clears payloads on success, terminal failure or expiry; ciphertext
may remain in the database until the worker resumes after an outage. Share only
minimum necessary details and avoid highly sensitive information.
Use /account only when you choose persistent Case tracking. Anonymous draft generation remains available without registration.
A pairing code is not a completed link. Confirm only in an authenticated account-linking screen that reports success; this screen is not yet part of every deployment.
A command being accepted does not mean a complaint was submitted to an authority.
"""
    if update.message:
        await update.message.reply_text(message)
