"""Initial authoritative India-law catalog for shared legal routing.

This is a routing/catalog layer, not a substitute for the full texts. Full
texts, amendments, rules and current notifications should be ingested from
primary official sources and versioned separately.
"""

from src.core.contracts.legal_knowledge import LegalKnowledgeItem, LegalKnowledgeStatus, LegalSourceTier


INDIA_CORE_LAW_CATALOG = (
    LegalKnowledgeItem("constitution-india", "Constitution of India", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/bitstream/123456789/16124/1/the_constitution_of_india.pdf", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("bsa-2023", "Bharatiya Sakshya Adhiniyam, 2023", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/20063", effective_from="2024-07-01", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("contract-act-1872", "Indian Contract Act, 1872", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/bitstream/123456789/2187/2/A187209.pdf", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("consumer-protection-2019", "Consumer Protection Act, 2019", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/indiacode/handle/123456789/15256", effective_from="2020-07-24", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("competition-act-2002", "Competition Act, 2002", LegalSourceTier.PRIMARY_LAW, "India", "https://www.cci.gov.in/legal-framwork/act", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("legal-services-authorities-1987", "Legal Services Authorities Act, 1987", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/bitstream/123456789/16128/1/198739.pdf", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("prevention-corruption-1988", "Prevention of Corruption Act, 1988", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/1558", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("lokpal-lokayuktas-2013", "Lokpal and Lokayuktas Act, 2013", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/2122", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("environment-protection-1986", "Environment (Protection) Act, 1986", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/1876", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("legal-metrology-2009", "Legal Metrology Act, 2009", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/2102", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("information-technology-2000", "Information Technology Act, 2000", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/handle/123456789/1999", status=LegalKnowledgeStatus.PENDING_REVIEW),
    LegalKnowledgeItem("digital-personal-data-protection-2023", "Digital Personal Data Protection Act, 2023", LegalSourceTier.PRIMARY_LAW, "India", "https://www.indiacode.nic.in/indiacode/handle/123456789/22037", status=LegalKnowledgeStatus.PENDING_REVIEW),
)
