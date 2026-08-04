from telegram import Update
from telegram.ext import ContextTypes

from tools.generate_pdf import generate_complaint_pdf


async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ------------------------------------
    # Validate Input
    # ------------------------------------

    if len(context.args) < 2:

        await update.message.reply_text(
            """
Usage

/complaint office_id issue

Example

/complaint 3 Aadhaar update delayed
"""
        )

        return

    # ------------------------------------
    # Read Arguments
    # ------------------------------------

    office_id = context.args[0]

    issue = " ".join(context.args[1:])

    # ------------------------------------
    # Generate PDF
    # ------------------------------------

    pdf = generate_complaint_pdf(

        user_name="Citizen",

        user_address="Not Provided",

        office_id=office_id,

        issue_text=issue,

    )

    # ------------------------------------
    # Reply
    # ------------------------------------

    await update.message.reply_text(

        f"""
✅ Complaint Generated Successfully

{pdf}

You can now submit this complaint to the concerned office.
"""
    )
