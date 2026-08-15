from typing import Dict, Any, List, Optional

# Static repository containing live bills, acts, and amendments for South and North East India.
# Includes automated compliance evaluations modeled around the Golden Triangle of the Indian Constitution.
LIVE_LEGISLATIVE_BILL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "BILL-2026-KL-04": {
        "title": "Kerala Public Spaces Regulatory (Amendment) Bill, 2026",
        "region": "South India",
        "state": "Kerala",
        "status": "PROPOSED_AMENDMENT",
        "summary": "Proposes stricter licensing rules for public assemblies and localized gatherings near municipal infrastructure corridors.",
        "constitutional_evaluation": {
            "is_compliant_with_golden_triangle": False,
            "article_14_analysis": "COMPLIANT: Standard rules applied equally across all local body zones.",
            "article_19_analysis": "VIOLATION DETECTED: The broad definition of gathering criteria places unreasonable restrictions on the freedom of speech and peaceful assembly guaranteed under Article 19(1)(a) and 19(1)(b).",
            "article_21_analysis": "COMPLIANT: No direct threat to life or personal liberty frameworks.",
            "overall_constitutional_summary": "NON-COMPLIANT. This amendment unconstitutionally restricts public participation rights by establishing arbitrary police licensing protocols over peaceful civic gatherings."
        }
    },
    "BILL-2026-AS-09": {
        "title": "Assam Digital Services and Identity Validation Act, 2026",
        "region": "North East India",
        "state": "Assam",
        "status": "PENDING_LEGISLATIVE_VOTE",
        "summary": "Requires digital identity tracking verification layers to access basic municipal public utilities and state infrastructure channels.",
        "constitutional_evaluation": {
            "is_compliant_with_golden_triangle": False,
            "article_14_analysis": "VIOLATION DETECTED: Creates arbitrary classifications between citizens with digital credentials and those without, violating equal protection principles.",
            "article_19_analysis": "COMPLIANT: Does not directly limit express freedoms.",
            "article_21_analysis": "VIOLATION DETECTED: Violates informational privacy protections under Article 21, failing the proportionality test established in the K.S. Puttaswamy judgment.",
            "overall_constitutional_summary": "NON-COMPLIANT. The bill fails fundamental proportionality tests by conditioning access to basic human needs on surveillance tracking protocols."
        }
    }
}

def fetch_active_bill_profile(bill_code: str) -> Optional[Dict[str, Any]]:
    """Retrieves verified legislative data profiles from the application layer memory."""
    return LIVE_LEGISLATIVE_BILL_REGISTRY.get(bill_code)
