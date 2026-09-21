import pytest
from src.security.input_policy import InputPolicyViolation, require_integer_range, require_text

def test_text_is_normalized_and_bounded():
    assert require_text("  hello  ", field="subject", max_length=10) == "hello"

def test_text_rejects_empty_and_oversized_values():
    with pytest.raises(InputPolicyViolation):
        require_text("   ", field="subject", max_length=10)
    with pytest.raises(InputPolicyViolation):
        require_text("01234567890", field="subject", max_length=10)

def test_integer_range_rejects_bool_and_out_of_range():
    with pytest.raises(InputPolicyViolation):
        require_integer_range(True, field="count", minimum=0, maximum=5)
    with pytest.raises(InputPolicyViolation):
        require_integer_range(9, field="count", minimum=0, maximum=5)
