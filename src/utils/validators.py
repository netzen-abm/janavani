import re
from pydantic import BaseModel, Field
from typing import Optional, Dict

class LegalDocumentSchema(BaseModel):
    """Rigid structural schema forcing JSON output format and blocking conversational chatter."""
    is_valid_civic_issue: bool = Field(description="False if input is conversational chat, greetings, search, or non-civic matter.")
    rejection_reason: Optional[str] = Field(None, description="Explanation if is_valid_civic_issue is False.")
    document_type: str = Field(description="Type of document, e.g., 'Complaint', 'RTI Request', 'Representation'")
    suggested_ministry_or_department: str = Field(description="Identified government department or public authority.")
    subject_line: str = Field(description="A concise, formal subject line in official government format.")
    factual_points: list[str] = Field(description="Numbered bullet points outlining the core facts parsed from the issue.")
    legal_or_policy_basis: list[str] = Field(description="Constitutional clauses, RTI acts, or regulatory frameworks relevant to the issue.")
    specific_prayers_or_requests: list[str] = Field(description="Explicit demands or solutions requested from the authority.")

class PrivacyPreservingTokenizer:
    """Removes sensitive identifiers locally before outbound LLM connection requests."""
    @staticmethod
    def deidentify_text(raw_text: str) -> Dict[str, str]:
        sanitized = raw_text
        
        # Regex mappings for sensitive Indian documentation patterns
        patterns = {
            r"\b\d{4}\s\d{4}\s\d{4}\b": "[REDACTED_AADHAAR]",
            r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b": "[REDACTED_PAN]",
            r"\b[A-Z]{3}\d{7}\b": "[REDACTED_PASSPORT]",
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b": "[REDACTED_EMAIL]",
            r"\b(?:\+91|0)?[6-9]\d{9}\b": "[REDACTED_PHONE]"
        }
        
        for pattern, replacement in patterns.items():
            sanitized = re.sub(pattern, replacement, sanitized)
            
        return {"sanitized_text": sanitized}

