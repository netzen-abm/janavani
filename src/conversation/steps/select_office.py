offices = find_offices(department, location)

# --------------------------------------
# ❌ NO OFFICE FOUND
# --------------------------------------

if not offices:

    await update.message.reply_text(
        "⚠️ No exact office found.\n\n"
        "You can still continue:\n\n"
        "1 → Enter office manually\n"
        "2 → Continue without office\n\n"
        "Reply with 1 or 2."
    )

    # Save intent
    session = get_session(update.effective_user.id)
    session["office"] = None

    # 👉 Move to next state (you will already have this)
    set_state(
        update.effective_user.id,
        "WAITING_FOR_OFFICE_FALLBACK"
    )

    return