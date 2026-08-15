import re
from pydantic import BaseModel, Field, field_validator

class OfficeFeedbackSchema(BaseModel):
    """Rigid verification structure for incoming citizen experience tracking inputs."""
    office_id: str = Field(..., description="Unique code of the targeted municipal office, e.g., 'KL-TVM-01'.")
    department_name: str = Field(..., description="Target department cluster, e.g., 'Revenue', 'Public Works'.")
    service_rating: int = Field(..., description="Numerical score mapping satisfaction bounds from 1 (poor) to 5 (excellent).")
    citizen_comment: str = Field(..., description="Text-based experience description provided by the user.")

    @field_validator("service_rating")
    @classmethod
    def validate_rating_bounds(cls, value: int) -> int:
        if not (1 <= value <= 5):
            raise ValueError("Rating values must fall strictly inside the 1 to 5 integer parameter space.")
        return value

class ContentSanitizationEngine:
    """Blocks adversarial payload elements and text strings locally."""
    
    # Simple explicit pattern matching structure for screening malicious content patterns
    BANNED_EXPRESSIONS = [r"\bidiot\b", r"\bcorrupt\b", r"\bcheat\b", r"<script>", r"javascript:"]

    @classmethod
    def sanitize_commentary(cls, raw_comment: str) -> str:
        # Strip out potential HTML/Script code tags completely to block cross-site scripting (XSS)
        cleaned_text = re.sub(r"<[^>]*>", "", raw_comment).strip()
        
        # Standardize spaces
        cleaned_text = " ".join(cleaned_text.split())
        
        # Enforce content length boundaries defensively
        if len(cleaned_text) > 300:
            cleaned_text = cleaned_text[:297] + "..."
            
        return cleaned_text

    @classmethod
    def is_safe(cls, text: str) -> bool:
        """Returns False if the string contains obvious injection attacks or explicit personal insults."""
        lowered_text = text.lower()
        for pattern in cls.BANNED_EXPRESSIONS:
            if re.search(pattern, lowered_text):
                return False
        return True
