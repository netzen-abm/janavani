from src.adapters.telegram.identity import identity_for_telegram_user

def test_telegram_identity_is_canonical_and_stable():
    first = identity_for_telegram_user(12345)
    second = identity_for_telegram_user(12345)
    assert first.principal.principal_id == "telegram:12345"
    assert first.principal.principal_id == second.principal.principal_id
    assert first.principal.interface == "telegram"

def test_telegram_identity_rejects_invalid_user():
    try:
        identity_for_telegram_user(0)
    except ValueError:
        return
    raise AssertionError("invalid Telegram identity must fail closed")
