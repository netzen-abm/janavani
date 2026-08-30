# JanaVani India Legal Intelligence Architecture

## Objective

JanaVani should be capable of understanding and routing civic matters against a broad Indian legal and procedural knowledge base. This does **not** mean silently training a model to memorize law. The authoritative legal corpus should be versioned, source-linked, jurisdiction-aware, and retrievable.

## Source hierarchy

1. Constitution and primary legislation
2. Rules, regulations, schedules and official notifications
3. Official departmental/commission guidance and forms
4. Verified judicial/tribunal/commission decisions where relevant
5. Practical secondary references, clearly attributed and never allowed to override primary law

## Initial high-value corpus

### Constitutional / public-law foundation
- Constitution of India
- Fundamental Rights, Directive Principles, constitutional offices and governance structure relevant to the case

### Evidence / digital records
- Bharatiya Sakshya Adhiniyam, 2023
- Information Technology Act, 2000 and relevant rules
- Digital evidence and record-integrity procedures

### Civic information / accountability
- Right to Information Act, 2005
- RTI Rules and applicable Central/State procedures
- Lokpal and Lokayuktas Act, 2013
- Prevention of Corruption Act, 1988
- Legal Services Authorities Act, 1987

### Consumer / market
- Consumer Protection Act, 2019
- Legal Metrology Act, 2009
- Competition Act, 2002 and CCI regulations/notifications

### Contracts / private transactions
- Indian Contract Act, 1872
- Appropriate sector-specific contract and sale/service laws as the matter requires

### Environment / public-interest matters
- Environment (Protection) Act, 1986
- Relevant environmental rules, notifications and sectoral legislation

### Privacy / technology
- Digital Personal Data Protection Act, 2023
- Information Technology Act, 2000 and applicable subordinate rules

## Additional corpus to add by domain

JanaVani should progressively add verified domain packs rather than attempting to load every Indian law into one undifferentiated corpus:

- municipal and panchayat law
- land and property
- revenue and records
- public distribution / food / welfare
- education
- health and public health
- labour and employment
- banking / insurance / financial services
- electricity / utilities
- roads / transport / motor vehicles
- housing / real estate
- environment / pollution
- disability rights
- senior citizens / child protection / women and family-related public services
- scheduled caste / scheduled tribe and other statutory protections
- elections and democratic participation
- government procurement and public works
- telecommunications / digital services

## Drafting capability

Legal knowledge and drafting skill are separate capabilities.

JanaVani should have structured drafting skills for:

- complaint letters
- representations
- RTI applications and appeals
- consumer complaints
- contractual notices and clauses
- information requests
- objections
- grievance representations
- escalation letters
- evidence-preservation records
- procedural checklists

Drafting must distinguish facts, allegations, evidence, legal propositions, requests/prayers, and procedural next steps. The system should not invent facts, citations, parties, deadlines, or legal conclusions.

## Contract drafting

A shared Contract Drafting capability should support structure and review rather than pretending to replace counsel. It should identify parties, definitions, scope, consideration, obligations, representations/warranties, conditions precedent, term, termination, confidentiality, IP, liability/indemnity, dispute resolution, governing law, notices, force majeure, amendment, assignment, severability and execution requirements where applicable.

The Indian Contract Act, 1872 is a primary source for the general contract framework; sector-specific statutes and current rules may materially change the result.

## Decision architecture

Legal intelligence should produce:

- applicable domain(s)
- candidate legal sources
- jurisdiction
- source status/version
- factual assumptions
- unresolved questions
- confidence/verification state
- recommended civic action(s)

It should not output an unqualified legal conclusion when the authoritative source or facts are insufficient.

## Privacy

Personal and sensitive information remains on the user's device by default. Legal reasoning should use the minimum necessary sanitized facts. Raw evidence should remain local unless an explicit, necessary, consented capability requires a minimized encrypted reference or artifact.

## AI

AI is a shared optional capability for the user. The legal knowledge system itself must remain available without AI. When AI is selected, retrieval should preferentially use the versioned authoritative corpus and expose provenance.

## Document boundary

After drafting/review, JanaVani delivers only the final PDF or editable DOCX selected by the citizen. JanaVani does not send, email, post, file, submit, or track the document after delivery.

## Reference principle

The practical RTI work of Prasanth Nair IAS, including *System Out Complete*, may inform question-formulation and civic-information workflow design with attribution. It is a practical reference, not primary law, and must never override authoritative sources.
