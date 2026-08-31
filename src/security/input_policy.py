"""Shared input bounds for anonymous/public capabilities."""


class InputPolicyViolation(ValueError):
    """Raised when capability input exceeds an explicit safety bound."""


def require_text(value: str, *, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise InputPolicyViolation(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise InputPolicyViolation(f"{field} must not be empty")
    if len(normalized) > max_length:
        raise InputPolicyViolation(f"{field} exceeds maximum length")
    return normalized


def require_integer_range(value: int, *, field: str, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise InputPolicyViolation(f"{field} must be an integer")
    if value < minimum or value > maximum:
        raise InputPolicyViolation(f"{field} is outside the permitted range")
    return value
