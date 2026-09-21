import re
from typing import Dict, Any, List, Optional

class AirGappedKnowledgeGuardrail:
    """
    Implements localized structural text scanning loops to lock LLM execution paths.
    Enforces absolute compliance with platform boundaries without external network dependencies.
    """
    # Deterministic lexical mapping anchors matching core legal frameworks
    VALID_CIVIC_ANCHORS = [
        r"\bbill\b", r"\bact\b", r"\bamendment\b", r"\bgrievance\b", r"\bcomplaint\b",
        r"\bpetition\b", r"\bland\b", r"\bgata\b", r"\bkhatoni\b", r"\brti\b", r"\boffice\b",
        r"\bofficer\b", r"\barticle\b", r"\bconstitution\b", r"\bcontract\b", r"\bagreement\b",
        r"\bpolice\b", r"\bcorruption\b", r"\bharassment\b", r"\bcleanliness\b", r"\bhospital\b"
    ]

    # Explicitly mapped statutory citation indexes for contextual prompt injection
    CONSTITUTIONAL_KNOWLEDGE_BASE = {
        "ARTICLE_14": "Article 14 guarantees Equality Before Law and Equal Protection of Laws within India.",
        "ARTICLE_19": "Article 19 guarantees Freedom of Speech, Expression, and Peaceful Assembly without Arms.",
        "ARTICLE_21": "Article 21 guarantees Protection of Life and Personal Liberty; includes Right to Informational Privacy.",
        "ARTICLE_51A": "Article 51A states the Fundamental Duties of every citizen to strive towards excellence and protect public property.",
        "BSA_2023": "Sections 74 & 75 of the Bharatiya Sakshya Adhiniyam, 2023 govern the admissibility of public/private electronic records."
    }

    @classmethod
    def verify_and_extract_context(cls, user_raw_input: str) -> Optional[Dict[str, Any]]:
        """
        Scans queries against allowed civic tracking parameters. Rejects out-of-scope chat 
        and extracts localized reference anchors for targeted model context injection.
        """
        cleaned_text = user_raw_input.lower().strip()
        
        # Step 1: Enforce Scope Validation (Catch out-of-scope chatbot use or searches)
        matched_scope = False
        for pattern in cls.VALID_CIVIC_ANCHORS:
            if re.search(pattern, cleaned_text):
                matched_scope = True
                break
                
        if not matched_scope:
            return None # Rejection signal: Query falls outside Janavani's operational scope

        # Step 2: Extract Relevant Legal Anchors for Contextual Injection
        injected_references = []
        if "equality" in cleaned_text or "14" in cleaned_text:
            injected_references.append(cls.CONSTITUTIONAL_KNOWLEDGE_BASE["ARTICLE_14"])
        if "freedom" in cleaned_text or "assembly" in cleaned_text or "19" in cleaned_text:
            injected_references.append(cls.CONSTITUTIONAL_KNOWLEDGE_BASE["ARTICLE_19"])
        if "life" in cleaned_text or "privacy" in cleaned_text or "liberty" in cleaned_text or "21" in cleaned_text:
            injected_references.append(cls.CONSTITUTIONAL_KNOWLEDGE_BASE["ARTICLE_21"])
        if "duty" in cleaned_text or "51" in cleaned_text:
            injected_references.append(cls.CONSTITUTIONAL_KNOWLEDGE_BASE["ARTICLE_51A"])
        if "evidence" in cleaned_text or "record" in cleaned_text or "sakshya" in cleaned_text:
            injected_references.append(cls.CONSTITUTIONAL_KNOWLEDGE_BASE["BSA_2023"])

        # Default fallback context if no explicit articles were named
        if not injected_references:
            injected_references.append("General constitutional petition structure under Preamble directives.")

        return {
            "is_valid_civic_intent": True,
            "matched_context_blocks": injected_references
        }
