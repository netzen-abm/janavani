import re
from pydantic import BaseModel, Field, field_validator


class OfficeFeedbackSchema(BaseModel):
    """Validated structure for incoming citizen service-experience feedback."""

    office_id: str = Field(..., description="Unique code of the targeted public office.")
    department_name: str = Field(..., description="Target department or service cluster.")
    service_rating: int = Field(..., description="Citizen-reported service rating from 1 (poor) to 5 (excellent).")
    citizen_comment: str = Field(..., description="Text-based experience description provided by the citizen.")

    @field_validator("service_rating")
    @classmethod
    def validate_rating_bounds(cls, value: int) -> int:
        if not 1 <= value <= 5:
            raise ValueError("Rating values must be between 1 and 5.")
        return value


class ContentSanitizationEngine:
    """Apply lightweight input screening without suppressing viewpoints or allegations."""

    # These patterns target explicit personal insults and obvious script injection.
    # Allegations such as "corrupt" must not be rejected solely for their viewpoint.
    BANNED_EXPRESSIONS = [
        r"\\bidiot\\b",
        r"\\bcheat\\b",
        r"<script>",
        r"javascript:",
    ]

    @classmethod
    def sanitize_commentary(cls, raw_comment: str) -> str:
        """Strip markup-like tags, normalize whitespace, and bound stored text."""
        cleaned_text = re.sub(r"<[^>]*>", "", raw_comment).strip()
        cleaned_text = " ".join(cleaned_text.split())
        if len(cleaned_text) > 300:
            cleaned_text = cleaned_text[:297] + "..."
        return cleaned_text

    @classmethod
    def is_safe(cls, text: str) -> bool:
        """Flag obvious injection or listed personal insults, not critical viewpoints."""
        lowered_text = text.lower()
        return not any(re.search(pattern, lowered_text) for pattern in cls.BANNED_EXPRESSIONS)
