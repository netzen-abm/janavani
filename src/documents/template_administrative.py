"""Curated administrative fee/levy evidence-demand template.

Generic structure only; never store citizen-specific values here.
"""
from src.documents.template_models import CivicDocumentTemplate, TemplateSection

_ADMINISTRATIVE_EVIDENCE_DEMAND = CivicDocumentTemplate(
        template_id="administrative.evidence-demand",
        version=1,
        title="Administrative notice reply — demand for documentary evidence",
        document_type="Administrative reply and documentary-evidence demand",
        purpose="Request the enabling law, jurisdiction, calculation, supporting records and procedural safeguards for an administrative fee, cess, levy or service charge.",
        jurisdiction_scope="India; verify the applicable Central, State or local law, disclosure rules and procedure before dispatch.",
        language="en",
        compatible_case_types=("objection", "non_consent", "representation", "complaint", "other"),
        required_fields=("subject", "issue", "jurisdiction"),
        optional_fields=(
            "proposal_or_notice",
            "part_i_interrogatories",
            "legal_framework",
            "requested_conditions",
            "requested_documents",
            "remedies_reserved",
            "references",
            "response_period",
            "deadline_date"
        ),
        sections=(
            TemplateSection("document_header", "Dispatch and party details — complete locally", (
                (
                    "Date: [Insert date of writing]\nReference: [Insert issuing notice number and date, if available]\nTo: [Insert the competent "
                    "authority's official name, designation, department and address]"
                ),
                (
                    "Copy to: [Insert relevant oversight authority or local body, if appropriate]\nDelivery: [Select an appropriate trackable "
                    "method and official email, if applicable]\nFrom / signature: [Complete locally; disclose only necessary personal details]"
                )
            )),
            TemplateSection("issue", "Administrative notice, fee or levy being challenged"),
            TemplateSection("proposal_or_notice", "Citizen's response or existing draft"),
            TemplateSection("part_i_interrogatories", "Part I — Foundational and constitutional questions", (
                (
                    "Foundational — Identify the exact Act, section, rule, notification or other primary legal instrument relied upon to authorize "
                    "the levy and create the alleged personal obligation, including its operative wording and effective date."
                ),
                (
                    "Foundational — Identify the competent authority and jurisdiction for imposing, assessing, collecting and recovering the "
                    "amount, including the legal basis for any penalties, arrears recovery or restriction on a service or licence."
                ),
                (
                    "Foundational — State whether the amount is classified as a tax, fee, cess or service charge; explain the enabling provision, "
                    "calculation method, cost basis and any proportionality assessment."
                ),
                (
                    "Foundational — Identify applicable exemptions, concessions, hardship protections, objections, appeals and safeguards before "
                    "penalties, service restrictions or recovery, citing the governing procedure."
                ),
                (
                    "Article 13, where applicable — Identify any recorded review of consistency with applicable constitutional protections and "
                    "provide any disclosable record; do not assume a review exists or that the provision is invalid."
                ),
                (
                    "Article 14 — Explain the objective criteria and supporting evidence used to set the amount and apply it across households, "
                    "localities, categories or similarly situated persons."
                ),
                (
                    "Articles 19(1)(g) and 19(6), if occupational or trade rights are affected — Identify the law and reasons relied upon to "
                    "connect non-payment with refusal or renewal of a licence or permit and state the review safeguards."
                ),
                (
                    "Article 21, where relevant to the alleged impact — Identify the legal basis and safeguards for any proposed denial of "
                    "service, intrusion or other material impact, including how hardship and due process are addressed."
                ),
                (
                    "Article 265, where the amount is tax-like or alleged to be a tax — Identify the authority of law relied upon and explain the "
                    "levy classification, charging provision and assessment process."
                ),
                (
                    "Article 300A, if property recovery or attachment is threatened — Identify the statutory recovery power, preconditions, "
                    "notice, hearing, appeal and due-process safeguards before any deprivation of property."
                ),
                (
                    "Article 51A(h), if scientific or technical justification is relied upon — Identify available studies, evidence, cost or "
                    "impact analysis, methodology and alternatives considered."
                )
            )),
            TemplateSection("legal_framework", "Potential constitutional and statutory provisions to verify", (
                (
                    "Potential references for jurisdiction-specific review include Articles 13, 14, 19(1)(g), 19(6), 21, 265, 300A and 51A(h) of "
                    "the Constitution of India. Include only provisions directly relevant to the facts and governing law; these references do not "
                    "establish that a levy is invalid."
                ),
                (
                    "For public-document classification and certified-copy requests, verify Bharatiya Sakshya Adhiniyam, 2023 sections 74–76 (in "
                    "force from 1 July 2024): these concern public/private documents, certified copies of documents a person has a right to "
                    "inspect, and proof by certified copies. They do not grant unrestricted access to every record; check the applicable "
                    "RTI/disclosure law, exemptions and any transitional rule before citing."
                )
            )),
            TemplateSection("requested_conditions", "Requested response and disclosure conditions", (
                "Please provide a point-by-point response and identify the legal instrument and record relied upon for each material conclusion.",
                (
                    "For a record not supplied, please identify any applicable exemption or other legal basis for withholding it and the available "
                    "review or appeal mechanism, to the extent required by law."
                ),
                "Please state the applicable statutory response period and objection or appeal process. A requested period in this letter is not automatically a statutory deadline.",
                (
                    "For records that the requester is legally entitled to inspect, please provide certified copies in the form prescribed "
                    "by applicable law and identify any applicable fee or process."
                ),
                (
                    "Please provide any prescribed certification of authenticity/completeness available under the governing procedure. "
                    "An affidavit is requested only where lawful and appropriate; do not assume one is mandatory."
                )
            )),
            TemplateSection("requested_documents", "Part II — Documents and records requested", (
                "Proposal and approval records for introduction or revision of the named levy, including disclosable note sheets, recommendations, objections and final decision records.",
                (
                    "Administrative sanction or order file, including the enabling provision, approval, calculation methodology, financial "
                    "rationale and legal vetting that may lawfully be disclosed."
                ),
                "Cabinet, ministerial or council records, if applicable and disclosable, showing consideration or approval.",
                "Relevant committee records, minutes, recommendations, dissent or recorded votes, where held and disclosable.",
                "Current rules, regulations, notifications, circulars and operational guidelines relied upon.",
                "Available legal opinions or departmental notes that may lawfully be disclosed; identify any exemption relied upon for withheld material.",
                "Government orders, contracts, memoranda and collection-agency arrangements, including accountability and audit provisions, subject to applicable disclosure law.",
                "Available studies, surveys, cost calculations, impact assessments and methodologies relied upon.",
                "Public notices, consultation or hearing records, submissions, minutes and responses to objections, where held and disclosable.",
                "Relevant legislative materials or debate records, if any and lawfully available, concerning the enabling provision or levy."
            )),
            TemplateSection("remedies_reserved", "Part III — Rights and remedies reserved", (
                (
                    "If no adequate response is received, I reserve any lawful administrative, statutory or judicial remedies available on the "
                    "facts and under applicable law. Non-response alone is not asserted here to constitute agreement, admission or waiver."
                )
            )),
            TemplateSection("references", "Notice references and supporting public references"),
            TemplateSection("response_period", "Requested response period (verify applicable deadlines)", (
                "Requested response period: [Insert a requested period; verify any binding statutory time limit and the proper channel.]"
            )),
            TemplateSection("deadline_date", "Requested date, if appropriate", (
                "Requested date: [Insert a date if appropriate; distinguish a requested target from a statutory deadline.]"
            )),
            TemplateSection("jurisdiction", "Public authority and jurisdiction")
        ),
        introduction=(
            "I write regarding the administrative notice or demand identified in the subject above. "
            "I request the legal authority, jurisdictional basis, classification, calculation, supporting "
            "records and procedural safeguards relied upon. This is a request for clarification, not a "
            "finding that the levy is invalid; verify every citation and the applicable disclosure "
            "procedure before sending."
        ),
        provenance=(
            "Adapted from the citizen-supplied Official Administrative Reply & Demand for Documentary "
            "Evidence; related canonical structural source: "
            "docs/templates/NOTICE_NON_CONSENT_CONDITIONAL_ACCEPTANCE_RESOLUTION.md. Personal and "
            "case-specific values are intentionally excluded."
        ),
    )
