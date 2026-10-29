# Legal Knowledge, Reusable Drafting, and Hisaab Interoperability Plan

**Status:** Proposed execution plan; not legal advice, not a partnership agreement  
**Reviewed:** 29 October 2026  
**Applies to:** Existing Janavani constitutional-governance policy, shared infrastructure contract, research/evidence provider contract, and canonical template-first drafting workflow

## 1. Decision

Do not start by fine-tuning a model on statutes or building a new legal-services subsystem. Prove a source-versioned retrieval-augmented generation (RAG) workflow around the existing template catalogue and civic-draft workflow. Use deterministic rules for form validation and workflow decisions; use a model only for bounded explanation or wording assistance after the privacy-safe input-minimization gate is implemented and tested.

Treat Hisaab as an independent, potentially complementary evidence atlas—not as a Janavani dependency and not as a source Janavani may publish or modify at will. Begin with an owner-approved, read-only evidence handoff based on already-published, source-backed records. Do not connect to Hisaab's Supabase database, use its private credentials, publish its candidate records, or send citizen narratives to Hisaab.

## 2. Existing boundaries to reuse

The repository already has relevant policy and implementation. Extend these rather than creating parallel registries or workflow engines:

- docs/JANAVANI_CONSTITUTIONAL_GOVERNANCE.md — constitutional framing, source-type distinctions, privacy, optional AI and user choice.
- docs/architecture/ECOSYSTEM_SHARED_INFRASTRUCTURE_CONTRACT.md — shared capability/security/provider contracts and independent access surfaces.
- docs/architecture/RESEARCH_EVIDENCE_ARCHIVAL_PROVIDER_CONTRACT.md — provider-neutral retrieval, provenance, source verification and graceful degradation.
- docs/architecture/CITIZEN_EVIDENCE_BOUNDARY_CONTRACT.md — citizen-controlled evidence, minimization and source provenance.
- src/documents/template_catalogue.py and the existing template definitions — the canonical reusable document formats.
- src/services/civic_draft_workflow.py — deterministic preview and common drafting policy.
- src/ui/civic_drafting.py — reused web presentation flow; it is not a second drafting engine.
- src/web/constitutional_router.py — existing constitutional-objection route and download-only contract.

The current candidate intentionally disables remote AI for arbitrary free-text citizen narratives and pasted drafts until minimization is proven. Legal-source retrieval does not override that restriction. Do not add raw citizen narratives to the legal corpus, model-training set, analytics, or external evidence-atlas requests.

## 3. What "train Janavani" should mean

Use five separate activities and prove them in this order.

### 3.1 Build and maintain the authoritative source corpus

Acquire official legal materials, current rules, notifications and source-linked judgments under their applicable reuse terms. Store immutable source snapshots only where retention and redistribution are permitted. Otherwise retain the official link, metadata, hash where lawful and feasible, retrieval locator, and version evidence.

Create a source record with, at minimum:

- stable source ID and source family;
- official title, issuing authority and canonical URL;
- Act/rule/notification/case identifier and issuing jurisdiction;
- publication, enactment, commencement, amendment and retrieval dates where applicable;
- applicable-from and applicable-until dates when established; never infer an unknown date;
- language, document edition, source hash, section/article locator and parent-child hierarchy;
- source-authority class, reuse/licence basis and retention constraints;
- verification status, reviewer, last verification and next-check trigger;
- supersession links, without deleting the prior historical version.

A PDF filename or web crawl timestamp is not a version statement. Extract and verify the document's own edition/cutoff notes and cross-check subsequent Gazette notifications before marking a source current. If the current version cannot be established, say so and mark the answer as limited.

### 3.2 Parse laws without destroying their structure

Parse the Constitution by Part, Article, clause, proviso, Explanation, Schedule and amendment note. Parse legislation by Act, Chapter, Section, subsection, clause, proviso, Explanation, illustration, Schedule and amendment/commencement note. Keep tables, exceptions, definitions and referenced provisions linked to their parents.

Do not rely on arbitrary fixed-size text chunks alone. A retrieval unit should normally be a legally meaningful provision with its hierarchy and adjacent context. Add cross-references as metadata, not fabricated text. Keep original text separate from extracted text, normalized text, translation and Janavani commentary.

### 3.3 Retrieve before generating

For a legal or civic-rights question:

1. establish the user's purpose, relevant jurisdiction and date of the event/request;
2. retrieve the relevant official version plus amendments, rules and notifications applicable to that date;
3. retrieve controlling interpretation only when needed and only from a source whose status and court/authority are identified;
4. present exact supporting provision references and a short source excerpt where permitted;
5. generate an explanation or draft only from the retrieved evidence and the user's expressly supplied facts;
6. validate required fields, dates, recipient and document type deterministically;
7. return an editable draft for citizen review; never submit, email or represent it as filed.

If retrieval yields no applicable source, sources conflict, or the operative version is unclear, stop short of a confident legal conclusion. Ask for the missing jurisdiction/date or tell the user the exact verification gap. Do not fill gaps with model memory.

### 3.4 Use model training only for the right problem

Do not fine-tune legal text into model weights as the first step. Fine-tuning is a poor substitute for amendment tracking, source citations or determining which rule was in force on a particular date.

The initial "training" work should be:

- curated source ingestion and structural parsing;
- retrieval/ranking evaluation;
- prompt and output-schema evaluation;
- a synthetic/consented test set of citizen intents mapped to approved template IDs and required fields;
- correction and citation-accuracy tests.

If a later fine-tuning experiment is justified, train only on synthetic or explicitly approved, de-identified examples of task classification, field extraction and format/style—not citizen case narratives, names, addresses, contact details, evidence or completed letters. Fine-tuning must never replace official-source retrieval.

### 3.5 Evaluate with a release gate

Create a manually reviewed evaluation pack across Constitution, RTI, evidence provenance and drafting, including adversarial cases with outdated versions, conflicting jurisdictions, missing facts, misquoted sections, fake case citations, misleading user assertions, prompt injection inside source documents, and requests to submit a document.

Track separately:

- exact section/article citation accuracy;
- whether each factual legal statement is supported by the cited text;
- current-version and effective-date accuracy;
- correct central/state/local jurisdiction;
- correct selection of existing-record RTI vs complaint/representation/petition;
- preservation of citizen intent without invented facts;
- privacy leakage, unsupported legal claims and prohibited action attempts.

Any invented provision/citation, misapplied effective date, leaked personal datum or false claim of filing is a release-blocking failure. A fluent answer is not a passing legal answer.

## 4. Initial official source set and limits

The following are authoritative starting points observed in the 29 October 2026 research pass. They are not permission to assume that each source has remained unchanged since its stated edition. The source registry must re-check current official material and Gazette updates before deployment.

### Constitution of India

- Official Legislative Department document index: https://www.legislative.gov.in/documents
- Official consolidated English/Hindi diglot edition: https://www.legislative.gov.in/static/uploads/2025/07/88cca69e868e50b217f855be2fb8bdba.pdf. Its cover states “The Constitution of India [As on 1st May, 2026]”; the preface says it incorporates amendments up to the Constitution (One Hundred and Sixth Amendment) Act, 2023. The document index also displays an English Constitution entry published 23 December 2025. Record the exact edition, language, cutoff and amendment coverage for each ingested file; before claiming currency, check later official amendment Acts/Gazette material rather than relying on the edition label alone.
- Primary uses: constitutional structure, rights/duties context and carefully qualified issue routing. A citizen complaint does not automatically establish a constitutional violation. Do not generate an Article-based conclusion unless the applicable text and relevant interpretation have been retrieved and the facts support the limited statement.

### Bharatiya Sakshya Adhiniyam, 2023 (BSA)

- India Code portal: https://www.indiacode.gov.in/ (the former `indiacode.nic.in` pages now redirect to this portal; resolve the Act through the current official search and record the final canonical URL at ingestion). Legacy indexed Act detail: https://www.indiacode.nic.in/indiacode/handle/123456789/20063?col=123456789%2F1362&view_type=search
- India Code official PDF shown during this review as consolidated “as on the 6th October, 2025”: https://www.indiacode.nic.in/bitstream/123456789/20063/1/aa202347.pdf
- India Code identifies Act No. 47 of 2023 and an enforcement date of 1 July 2024. Verify later amendment/commencement notifications as part of source refresh.
- BSA covers rules and principles of evidence for judicial proceedings in its statutory scope. It is not part of the Constitution, and Janavani must not imply that every citizen attachment or administrative complaint is thereby proved admissible or compliant with evidence law.
- Janavani may preserve source, timestamp, hash, chain-of-handling events and transformation history as evidence provenance. Those technical records are not a legal determination of admissibility, authenticity or sufficiency.

### Right to Information Act, 2005 and rules

- India Code portal: https://www.indiacode.gov.in/ (the former `indiacode.nic.in` pages now redirect to this portal; resolve the Act through the current official search and record the final canonical URL at ingestion). Legacy indexed Act detail: https://www.indiacode.nic.in/indiacode/handle/123456789/17520?col=123456789%2F2510&view_type=search
- India Code official PDF: https://upload.indiacode.nic.in/showfile?actid=AC_CEN_26_36_00004_200522_1517807322955&filename=a2005-22.pdf&type=actfile. Its cover says “As on the 18th November, 2025” and its list of amending Acts includes the Digital Personal Data Protection Act, 2023 (22 of 2023).
- Central Information Commission Act/rules index: https://cic.gov.in/rti_act and notifications: https://cic.gov.in/rti-notifications
- Do not freeze the 2025 consolidated copy as the law through October 2026. Check later Central Gazette amendments, applicable RTI Rules and fee rules, and relevant State rules/orders before stating a current procedure or deadline. In particular, apply the commencement history of DPDP Act section 44(3) to RTI section 8(1)(j); do not use a pre-amendment RTI text for a question arising after the amendment took effect.
- RTI drafting must request existing records with a clearly named public authority, relevant period and specific record descriptions. Do not disguise a request for a newly authored explanation, opinion or remedy as a request for existing records. Validate jurisdiction and applicable procedure. Fee, CPIO/FAA routing, exemptions, third-party process, timelines and appeals must be grounded in the correct central/state/local rules and current official routing information.
- A PIB release dated January 2026 noted central RTI-cell decentralization to section-level CPIOs/FAAs effective in October 2025 for the described department. Treat this as a department-specific administrative update, not as a universal amendment to the RTI Act or a substitute for the relevant authority's current directory.

### Digital Personal Data Protection Act, 2023 (DPDP) — mandatory RTI temporal dependency

- Official MeitY/India Code Act copy: https://www.indiacode.nic.in/bitstream/123456789/22037/1/a2023-22.pdf
- Official Gazette commencement notification G.S.R. 843(E), dated 13 November 2025: https://egazette.gov.in/WriteReadData/2025/267647.pdf
- Official DPDP Rules, 2025 and commencement/corrigendum listing: https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025

The official commencement notification brought DPDP Act section 44(3) into force on 13 November 2025. That provision substitutes RTI Act section 8(1)(j) with the text “information which relates to personal information”. The RTI consolidated Act dated 18 November 2025 lists DPDP Act 2023 as an amending Act. This linkage is a material legal knowledge dependency and must be reflected in source versioning, retrieval and RTI-draft review.

Do not infer that every substantive DPDP obligation became operative on 13 November 2025. The same official commencement notification phases different DPDP provisions: it assigns specified provisions to the notification date, another group to one year after publication, and a further group to eighteen months after publication. The official DPDP Rules page also lists a 16 December 2025 corrigendum and an 18-month implementation timeline. The legal corpus must represent each provision/rule's own effective date and verify amendments/corrigenda, rather than assign one commencement date to the whole Act or Rules.

For RTI drafting, the engine must retrieve the amended clause applicable to the relevant date, and must not reuse an older template note or generated explanation describing the former text of section 8(1)(j) as current. Any advice about exemptions, public-interest considerations, severability or appeal strategy requires the operative statutory text and current authoritative interpretation; do not extrapolate from the amendment's short wording alone.

For JanaVani's own privacy architecture, treat DPDP-related compliance analysis as a separate, current legal workstream: data inventory, purpose limitation, notice/consent and withdrawal semantics, retention, processor/provider disclosures, access control, deletion and incident handling must be mapped to the exact provisions/rules and their respective phased commencement. Do not claim full statutory compliance merely because a consent checkbox or privacy notice exists.

### DPDP update — Removal of Difficulties Order, 2026

As of the 29 October 2026 review, MeitY's official “What's New” page lists the **Digital Personal Data Protection (Removal of Difficulties) Order, 2026**: https://www.meity.gov.in/whats-new. The official-hosted PDF is linked at https://www.meity.gov.in/static/uploads/2026/10/daf495a7b5798a3dfa72a944b51fc176.pdf; fetch it, record its hash and verify its Gazette publication metadata during corpus ingestion.

The order is identified as S.O. 5458(E), made on 5 October 2026 and published in the Gazette on 6 October 2026 in the sources reviewed. The reported operative changes are limited to two textual substitutions:
- DPDP Act section 9(1): “child or a person with disability” becomes “child or of a person with disability”, clarifying the parallel categories for which parent/lawful-guardian verifiable consent is specified.
- DPDP Act section 10(2)(c)(ii): “audit” becomes “data audit”.

This is a required version in the corpus, not evidence that sections 9 and 10 became operative immediately. Under G.S.R. 843(E), sections 9 and 10 were placed in the eighteen-month commencement tranche. Preserve the 2026 order date and publication date separately from the substantive provisions' commencement dates; calculate a prospective date only from the applicable official notification and re-verify it before presenting it to a user. Do not use this order to state that the entire DPDP Act or every DPDP Rule is currently in force.

The current knowledge graph must therefore link: (a) DPDP Act section 44(3) commencement on 13 November 2025; (b) the corresponding versioned RTI Act section 8(1)(j) text; (c) the DPDP Rules, 2025 and the 16 December 2025 corrigendum; (d) the 2026 Removal of Difficulties Order affecting sections 9(1) and 10(2)(c)(ii); and (e) each provision's separate commencement state. A question about RTI personal-information exemptions, children, persons with disabilities or significant-data-fiduciary audits must retrieve the applicable text and effective-date metadata rather than relying on the model's memorized version.

### Next legal domains: regulator-aware legal knowledge modules

This is a staged ingestion and validation register, not a representation that every listed Act, regulation, rule, notification or remedy has already been ingested or reviewed. For each item, capture the current official text, amendments, rules/regulations, commencement and transitional provisions, jurisdiction, competent authority, appeal forum, limitation periods, forms/fees, source hash and retrieval date. Do not infer that a named regulator has jurisdiction over every grievance in its industry.

#### Competition law and corporate-market conduct

- **Competition Act, 2002 (as amended)** — cover anti-competitive agreements (including section 3), abuse of dominant position (section 4), and combinations (sections 5–6), plus current regulations, thresholds, notifications, exemptions, procedure and remedial orders. The CCI's official antitrust page distinguishes prohibited conduct and explains that mere dominance is not itself prohibited; the question is abuse. Use this for issue triage and drafting of evidence requests, not for declaring an enterprise guilty. Sources: [India Code — Competition Act](https://www.indiacode.nic.in/indiacode/bitstream/123456789/2010/7/A2003-12.pdf), [CCI — Antitrust](https://cci.gov.in/antitrust), [CCI — Combination framework](https://www.cci.gov.in/combination/), [CCI — Legal framework and 2023 amendment](https://cci.gov.in/public/legal-framwork/act).
- **Competition Commission of India (CCI)** — keep CCI procedure, current regulations, directions and published decisions in the institutional layer.
- **National Company Law Appellate Tribunal (NCLAT)** — model the statutory appeal route for CCI orders separately from initial CCI filing or investigation. Check the current Competition Act provisions, NCLAT rules, e-filing instructions, forum, limitation and filing checklist for each matter. Sources: [NCLAT — appeals checklist](https://nclat.nic.in/downloads/check-list-appeals), [NCLAT — Act and Rules](https://nclat.nic.in/act-rules).

#### Sector regulation: routing matters to the correct authority

- **Telecommunications — TRAI / TDSAT:** source the Telecom Regulatory Authority of India Act, 1997, current TRAI regulations, directions and service-specific consumer procedures. Distinguish TRAI's regulatory role from dispute adjudication and appeals handled by the appropriate tribunal/forum; don't route every individual bill or service problem directly to TRAI. Source: [TRAI official history and statutory background](https://trai.gov.in/about-us/history).
- **Banking, payments and regulated financial services — RBI:** retrieve the Reserve Bank of India Act, 1934, Banking Regulation Act, 1949, the legislation applying to the specific product/entity, current directions/circulars and applicable complaint/ombudsman process. Identify the regulated entity and transaction type before recommending an escalation. Source: [RBI — legislative framework (official handbook)](https://website.rbi.org.in/documents/d/rbi/handbookg27022025d0f3f53f5d3c4310a6bb2f8ac2175d3a).
- **Petroleum and natural gas — PNGRB:** ingest the Petroleum and Natural Gas Regulatory Board Act, 2006 and current regulations/orders; preserve its statutory scope and exclusions. Source: [PNGRB — Act](https://www.pngrb.gov.in/eng-web/the_act.html).
- **Civil aviation — DGCA / Ministry of Civil Aviation:** include the Bharatiya Vayuyan Adhiniyam, 2024 (effective 1 January 2025 per the official Act copy), current rules, Civil Aviation Requirements, orders and notices. Do not treat the historical Aircraft Act, 1934 as the sole current parent statute after the new Act took effect. Map whether a matter belongs with DGCA, an operator, airport authority, accident-investigation body, security authority or another statutory forum. Sources: [India Code — Bharatiya Vayuyan Adhiniyam, 2024](https://www.indiacode.nic.in/indiacode/handle/123456789/20589?view_type=browse), [DGCA — Acts, Rules and regulatory material](https://www.dgca.gov.in/digigov-portal/?page=civilAviationRequirementPDF).

#### Environmental protection, pollution, conservation and project clearance

- **Environment (Protection) Act, 1986:** include rules, standards, notifications, directions and amendments, not only the parent Act. Source: [India Code — Environment (Protection) Act](https://www.indiacode.nic.in/indiacode/handle/123456789/1876?view_type=browse).
- **Water (Prevention and Control of Pollution) Act, 1974** and **Air (Prevention and Control of Pollution) Act, 1981:** model the Central Pollution Control Board (CPCB), State Pollution Control Boards (SPCBs), state-specific amendments/rules where applicable, consents, monitoring/inspection records and the actual statutory appeal path. Source: [India Code — Water Act](https://www.indiacode.nic.in/indiacode/handle/123456789/1612?col=123456789%2F1362&view_type=search), [India Code — Air Act](https://www.indiacode.nic.in/indiacode/handle/123456789/1389?view_type=browse), [CPCB](https://cpcb.nic.in/).
- **Wild Life (Protection) Act, 1972:** track the amended Act, schedules, rules and competent wildlife authorities. Source: [India Code — Wild Life (Protection) Act](https://www.indiacode.nic.in/indiacode/handle/123456789/1726?col=123456789%2F1362&view_type=search).
- **Forest law:** the law historically referred to as the Forest (Conservation) Act, 1980 was renamed the **Van (Sanrakshan Evam Samvardhan) Adhiniyam, 1980** by the 2023 amendment, effective 1 December 2023. Index the current title and retain historical-name aliases for search; check the applicable land definition, amendments, rules, directions and judicial decisions before advising. Source: [India Code — Van (Sanrakshan Evam Samvardhan) Adhiniyam, 1980](https://www.indiacode.nic.in/indiacode/handle/123456789/1760?sam_handle=123456789%2F1362&view_type=browse).
- **Biological Diversity Act, 2002:** incorporate the Biological Diversity (Amendment) Act, 2023 and its commencement notification (effective 1 April 2024), plus current rules and the competent National/State Biodiversity Board / local body roles. Source: [India Code — Biological Diversity Act](https://www.indiacode.nic.in/indiacode/handle/123456789/2046?view_type=browse), [official commencement notification](https://upload.indiacode.nic.in/showfile?actid=AC_CEN_16_18_000010_200318_1517807327125&filename=notification_bd_act%2C_2023.pdf&type=notification).
- **National Green Tribunal Act, 2010:** include jurisdiction, limitation, appealable instruments, benches, rules, applicable schedules and current precedents. The NGT is not a general first-stop forum for every environmental concern. Source: [India Code — NGT Act](https://www.indiacode.nic.in/indiacode/handle/123456789/2025?view_type=browse), [NGT — jurisdiction and role](https://www.greentribunal.gov.in/about-us).
- **Environmental Impact Assessment (EIA):** ingest the EIA Notification, 2006 (S.O. 1533(E)), all applicable amendments/corrigenda and current PARIVESH/Ministry/SEIAA procedural material. Preserve project category, threshold, location, competent clearance authority, consultation requirements and operative notification date. Do not treat a draft notification as operative law. Sources: [PARIVESH — EIA Notification 2006 and related notices](https://cpc.parivesh.nic.in/SingleWindow.aspx), [MoEFCC](https://moef.gov.in/).

#### How these modules connect to civic drafting

Every domain should share a common case-independent drafting contract but retain domain-specific, versioned rule packs. An RTI model asks for identifiable existing records; a regulatory complaint should identify the service/product, regulated entity, prior grievance channel, records, requested action and applicable authority. An environmental representation/complaint may require location, project/activity, dates, affected media (air/water/land/noise/biodiversity), available records, consent/clearance references and urgent risks. A competition-law submission may require market/context, conduct, actors, time period and documentary evidence; the system must avoid asserting a violation without evidence and legal review.

The router must distinguish (1) a request for information or existing records, (2) a service grievance, (3) a statutory complaint, (4) a regulatory representation, (5) an appeal, and (6) legal proceedings. It should ask only the minimum questions necessary, explain uncertainty, show why an authority was selected, and offer a user-reviewed alternative when forum/jurisdiction is unclear.

### Source hierarchy

Prefer official legislation, Gazette amendments, official rules/notifications, and official court judgments. Use official ministry/authority pages for their published procedure and records. Secondary commentary can aid discovery but cannot silently overwrite primary law. Clearly label translations, unofficial summaries, AI explanations and user claims.

## 5. Reusable legal and civic letter models

Store one content-free structural model, not one copy of every completed letter.

A reusable model may contain:

- template ID, schema version and language;
- document purpose/type and jurisdiction requirements;
- ordered section IDs and approved generic wording;
- required/optional fields, limits and validation rules;
- references to source provisions or drafting notes, with verification/version metadata;
- test cases and known limitations.

It must not contain completed citizen narratives, applicant names, addresses, phone/email, signatures, case IDs, evidence, account identifiers or other personal/sensitive data. The safe default is not to save an individual user's custom model globally: offer an explicit, separate save action to save an approved structure to that user's chosen storage, subject to a retention/deletion contract. Public/global templates require editorial review and version approval.

Reuse a model by deterministic field filling first. Ask AI only for a bounded improvement that demonstrably adds value. Store user corrections as ephemeral evaluation feedback by default; do not convert them to training data without a separate lawful basis, appropriate disclosure and consent. Version changes must be reviewable and rollback-capable.

Initial format catalogue:
- complaint/grievance: issue and requested corrective action;
- RTI: public authority, time range and existing records requested;
- representation/petition: position, factual basis, request and attachments list;
- administrative notice/evidence demand: notice reference, asserted demand, document requests and requested point-by-point response;
- constitutional-objection format: relevant measure/source, citizen comments and carefully qualified grounds.

The citizen remains the factual authority for their own account. Janavani must not invent dates, events, legal provisions, citations, authorities, evidence, deadlines or statements that silence creates agreement. The preview ends in review/download; the citizen sends it independently.

## 6. Hisaab: observed state and complementarity

Repository reviewed: https://github.com/theadiram/Hisaab, default branch main. Its README describes Hisaab as a source-backed public development evidence atlas. Its source code and project documentation are MIT-licensed, but its LICENSING.md explicitly leaves government records, datasets, maps, photographs, fonts and other third-party material under their respective reuse terms.

Observed in the Hisaab README/source tree during this review:

- Hisaab uses a separate Next.js/TypeScript application and Supabase-oriented data model. Its APIs include read routes for works, funding and coverage, plus protected administration and evidence-intake routes.
- Hisaab's README states that public release is blocked; its then-current summary describes 812,976 preserved historical locations, 86 reviewed PIB funding facts and zero published project/payment cards. The coverage API route also returns releaseReady=false.
- Hisaab's intake contract is versioned as hisaab-intake/1 and requires provenance such as source URL/hash, retrieval metadata, reuse basis, official project identifiers and explicit evidence gaps. Collector-supplied records cannot self-approve publication.
- Its evidence-publication path distinguishes a useful reviewed sanction/contract fact from a verified individual payment or completed project. Unknown payment/completion stages must remain unknown.
- Its launch-readiness document says Netlify deployment/DNS cutover had not happened at that document's checkpoint. The live adiram.me site could not be independently fetched in this review. Recheck its actual public release/deployment state directly with the owner before linking or describing it as live.

These are promising complementary responsibilities, not grounds to copy Hisaab data or access its private storage. Hisaab's candidate evidence is not automatically public or approved merely because code is open source.

## 7. Proposed integration boundary with Hisaab

### Appropriate division of responsibility

- **Hisaab:** source-backed development/funding/project records, documentary provenance, jurisdiction/coverage, financial interpretation, correction/withdrawal and its own publication decision.
- **Janavani:** citizen-intent clarification, finding the right civic/RTI/complaint pathway, drafting an editable request using reusable structures, optional Case-bound workflow, citizen review and citizen-controlled submission.
- **Shared boundary:** a versioned, read-only, source-linked record contract for evidence that Hisaab has explicitly published and authorized for reuse.

Never share database credentials, reuse Hisaab administrator sessions, write directly to its Supabase tables, mirror its private intake queue, or treat a link to a source as proof that a project/payment claim has passed Hisaab review.

### Suggested staged collaboration

**Stage 0 — owner-to-owner design review.** Propose a short discussion with the Hisaab maintainer. Confirm desired collaboration, public release status, API stability, source/data rights, correction/withdrawal procedure, attribution, rate limits and acceptable contribution method. No code or data access change is required for this stage.

**Stage 1 — public-link handoff only.** After Hisaab confirms a record is released, Janavani may link a user-selected project/funding receipt to its Hisaab page and its underlying official sources. Display Hisaab's stated evidence state, coverage cutoff and unknown stages without paraphrasing unknowns as facts. Add no identity or case narrative to the URL.

**Stage 2 — read-only public contract.** If the maintainer agrees, define and version a small public record schema/API or export containing: stable Hisaab record ID; record type; title; official project identifiers; jurisdiction and financial period; verified claim/stage and explicit unknowns; source IDs/URLs, locators, hashes and retrieval timestamps; reuse/attribution basis; publication version/status; last-reviewed time; correction/withdrawal pointer. Publish only approved public fields. Require tests for withdrawn records, stale versions, missing source links, pagination, rate limits and API outage.

**Stage 3 — evidence-gap to citizen request.** When a published Hisaab receipt explicitly marks a missing record, Janavani may offer a citizen-controlled RTI draft based on that missing existing record—after the user confirms the authority, jurisdiction and request scope. Pass the public record ID/source links only. Keep citizen narrative, identity, attachments, private Case and draft out of Hisaab.

**Stage 4 — contributor handoff, only by agreement.** Janavani or a participating citizen may prepare a Hisaab intake batch using the existing hisaab-intake/1 contract for public records gathered lawfully. Include original source reference, checksum, locator, reuse basis, jurisdiction and explicit gaps. Send through a maintainer-approved private contribution channel. The batch remains a candidate; Hisaab's own reviewers decide approval/publication. Do not automate submissions or publish data from Janavani directly to Hisaab.

### Independence and failure behavior

Janavani must still draft and export an RTI when Hisaab is unavailable. Hisaab must keep collecting and reviewing public evidence when Janavani is unavailable. Cache only public records with explicit source/version/freshness metadata. On API failure, show a source-unavailable notice and a link to the last known public record only if its withdrawal/freshness semantics are safe; never fabricate a zero or current-status claim.

## 8. First collaboration message to the Hisaab maintainer

Approach as a proposal, not an assumption that a partnership exists. Suggested agenda: (1) exchange goals and current release status; (2) inspect one published/approved record and the public source chain; (3) agree a minimal read-only record contract and attribution/withdrawal policy; (4) choose one pilot jurisdiction/project; (5) review whether Janavani can help citizens draft requests for genuinely missing existing records; (6) define owner approvals, issue tracking and a rollback path. No shared credentials, paid service, publication or DNS change should be part of an initial pilot.

## 9. Delivery sequence and stop conditions

1. Confirm the actual latest official editions and update the source registry before any answer is advertised as current law.
2. Add deterministic source/version metadata and retrieval tests around the existing workflow; do not create a second template catalogue.
3. Build an expert-reviewed synthetic evaluation set and citation/veracity gates.
4. Keep remote AI disabled for raw citizen narratives until minimization, provider disclosure and adversarial tests pass.
5. Pilot the public-link handoff only after Hisaab records are genuinely public and the maintainer confirms acceptable use.
6. Add a read-only adapter only after a versioned public contract and published sample record are agreed.
7. Keep cross-project collaboration optional and independently deployable. No release should depend on Hisaab availability.
8. Keep PR #226 in Draft until the latest code CI is green and staged Web/API/Telegram/PostgreSQL acceptance proves the intended routes and failure behavior.

Do not advance if a source's currentness, jurisdiction, reuse terms or claimed evidence status is unknown; if a user-private datum would cross to Hisaab or a model provider; or if any flow can represent a draft as filed/submitted without a citizen action.

### Alpha and beta release gates

**Closed alpha — may begin only when:** the exact release commit has green CI/security/dependency checks; the WebApp and Dynamic Web load with the approved logo/favicon and no visible CSS or duplicate-title defects; the six core template types produce deterministic drafts; RTI templates request existing records and require a competent public authority/jurisdiction; consent rejection is proven; user-entered content is not written to durable shared storage or logs; documents remain review/download only; and a small invited cohort has a feedback/reporting path. Alpha is a controlled usability and safety evaluation, not an assertion that the entire legal corpus is complete.

**Public beta — requires additional evidence:** repeated release-candidate tests across supported browsers/mobile layouts; versioned official source corpus for the publicly enabled domains; reviewed sample outputs and citation/commencement checks; adversarial tests for fabricated citations, wrong forum, prompt injection and misleading confidence; privacy threat assessment and data-flow/retention disclosure; dependency/licence audit; accessibility review; incident/support and rollback procedures; and staged integration tests proving Telegram webhook retries/idempotency, database outage recovery and surface independence. Public beta should start with only the domain modules that meet these gates. Do not enable all listed regulators simply because their names have been added to the roadmap.

**Fine-tuning gate:** do not fine-tune on production citizen narratives or user letters. First use curated, rights-cleared, expert-reviewed synthetic/de-identified examples only where a measured gap remains after template retrieval and prompt/rule improvements. Evaluate exact-source citation, section accuracy, jurisdiction/venue routing, completeness, unsupported assertions, privacy leakage and language robustness. Keep source retrieval and legal-version checks active after any tuning.



## 10. Reference links checked in this review

- Legislative Department official documents index — https://www.legislative.gov.in/documents
- India Code: Bharatiya Sakshya Adhiniyam, 2023 — https://www.indiacode.nic.in/indiacode/handle/123456789/20063?col=123456789%2F1362&view_type=search
- India Code: Right to Information Act, 2005 — https://www.indiacode.nic.in/indiacode/handle/123456789/17520?col=123456789%2F2510&view_type=search
- Central Information Commission: RTI Act and rules — https://cic.gov.in/rti_act
- MeitY/Gazette: DPDP Act section 44(3) commencement and RTI amendment — https://egazette.gov.in/WriteReadData/2025/267647.pdf
- MeitY: DPDP Rules 2025, commencement timeline and corrigendum — https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025
- MeitY official index for the DPDP (Removal of Difficulties) Order, 2026 — https://www.meity.gov.in/whats-new
- MeitY-hosted DPDP (Removal of Difficulties) Order, 2026 PDF — https://www.meity.gov.in/static/uploads/2026/10/daf495a7b5798a3dfa72a944b51fc176.pdf
- Hisaab repository — https://github.com/theadiram/Hisaab
- Hisaab data acquisition contract — https://github.com/theadiram/Hisaab/blob/main/docs/data-acquisition-contract.md
- Hisaab evidence publication path — https://github.com/theadiram/Hisaab/blob/main/docs/evidence-publication-path-2026-10-25.md
- Hisaab licensing — https://github.com/theadiram/Hisaab/blob/main/LICENSING.md
