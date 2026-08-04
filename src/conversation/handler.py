from telegram import Update
from telegram.ext import ContextTypes

from tools.search_directory import search_office
from tools.rate_office import save_rating
from tools.generate_pdf import generate_complaint_pdf

from conversation.state import (
    get_state,
    set_state,
    clear_state,
)

from conversation.session import (
    get_session,
    clear_session,
)

from conversation.constants import (
    NEW,
    WAITING_FOR_DOCUMENT,
    WAITING_FOR_DISTRICT,
)


# --------------------------------------------------
# /start
# --------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
"""
🇮🇳 Welcome to Janavani

Citizen Governance Platform

Available Commands

/start
/search
/rate
/complaint

Or simply type your issue.

Example

There is a broken road near my house.
"""
    )


# --------------------------------------------------
# /search
# --------------------------------------------------

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:

        await update.message.reply_text(
            "Usage:\n/search ration Kochi"
        )

        return

    department = context.args[0]
    location = " ".join(context.args[1:])

    result = search_office(
        department,
        location
    )

    await update.message.reply_text(result)


# --------------------------------------------------
# /rate
# --------------------------------------------------

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 3:

        await update.message.reply_text(
            "Usage:\n/rate 3 1 Aadhar failed"
        )

        return

    office_id = context.args[0]
    rating = int(context.args[1])

    issue = " ".join(context.args[2:])

    result = save_rating(
        office_id,
        rating,
        issue,
    )

    await update.message.reply_text(result)


# --------------------------------------------------
# /complaint
# --------------------------------------------------

async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Complaint generation will be connected to the conversation flow."
    )


# --------------------------------------------------
# Conversation
# --------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_message = update.message.text.strip()

    state = get_state(user_id)

    session = get_session(user_id)

    print("=" * 50)
    print("USER:", user_id)
    print("STATE:", state)
    print("MESSAGE:", user_message)
    print("=" * 50)

    # ----------------------------------

    if state == NEW:

        session["issue"] = user_message

        set_state(
            user_id,
            WAITING_FOR_DOCUMENT
        )

        await update.message.reply_text(
f"""
✅ Your issue has been recorded.

Issue

{session["issue"]}

----------------------------------

Select document

1️⃣ Complaint

2️⃣ RTI

Reply

1

or

2
"""
        )

        return

    # ----------------------------------

    if state == WAITING_FOR_DOCUMENT:

        if user_message == "1":

            session["document"] = "Complaint"

        elif user_message == "2":

            session["document"] = "RTI"

        else:

            await update.message.reply_text(
                "Please reply with 1 or 2."
            )

            return

        set_state(
            user_id,
            WAITING_FOR_DISTRICT
        )

        await update.message.reply_text(
f"""
Document Selected

✅ {session["document"]}

Now enter your District.

Example

Ernakulam
Kozhikode
Kannur
"""
        )

        return

        # ----------------------------------

    if state == WAITING_FOR_DISTRICT:

        session = get_session(user_id)

        session["district"] = user_message

        from services.office_service import find_offices

        offices = find_offices(
            session["issue"],
            session["district"]
        )

        if len(offices) == 0:

            await update.message.reply_text(
                f"""
District recorded:

{session['district']}

⚠️ No matching office found.

(Office search will become smarter soon.)
"""
            )

        else:

            office_list = ""

            for index, office in enumerate(offices, start=1):

                office_list += (
                    f"{index}. "
                    f"{office['office_name']}\n"
                )

            await update.message.reply_text(
                f"""
I found these offices.

{office_list}

Reply with the office number.
"""
            )

        clear_state(user_id)

        return
