# Document Template and Correction System

## Current implementation

The template contract/value objects are defined in `src/documents/template_models.py`,
curated, content-free definitions live in `src/documents/template_definitions.py`,
and `src/documents/template_catalogue.py` owns lookup and version resolution.
The catalogue provides complaint, public-service grievance, RTI, representation,
petition, and administrative evidence-demand structures. The last was curated from
the citizen-supplied “Official Administrative Reply & Demand for Documentary Evidence”
format. It stores no citizen names, addresses, notice identifiers, narrative, evidence,
or completed letter.

`src/services/civic_draft_workflow.py` composes the same deterministic preview for
WebApp and Telegram and may request optional, consent-gated AI wording improvements.
The AI response is accepted only through a bounded output schema. Both surfaces
derive the available template IDs and titles from the same catalogue.

The catalogue is source-controlled and curated. Persistent user-saved custom formats,
shared promotion of user-created formats, and model-training from edits are not
implemented. The four archived empty legacy document modules are not alternate
drafting engines; preserve their archive evidence unless a separate audit authorizes
a future change.

## Template contract

Every template declares purpose, document type, jurisdiction scope, language, version,
required and optional fields, ordered sections, provenance and review status. A template
is a reusable structure with editable, reviewed starter content—not immutable legal
wording. Complaint/grievance requests, RTI requests for existing records, and
administrative fee/levy evidence-demand replies remain distinct flows.

The administrative evidence-demand template is jurisdiction-aware. It asks for the
legal instrument, authority and jurisdiction, levy classification/calculation, applicable
procedures, relevant documentary evidence, and any available objection or appeal route.
Its generic questions and record requests are starter content for citizen review; they
are not legal findings and do not assert that a levy is invalid, that all requested
records must be disclosed, or that silence creates consent/agreement.

Its statutory prompts require review before use. In particular, Bharatiya Sakshya
Adhiniyam, 2023 sections 74–76 distinguish public/private documents, certified copies
of documents a person has a right to inspect, and proof by certified copies. They do
not grant unrestricted access to every record; the applicable RTI/disclosure law,
exemptions and any transitional issue must be checked for the actual request.

The structural model may contain labels, generic starter wording and allow-listed
section identifiers. It must not contain citizen names, postal addresses, contact
details, account identifiers, raw narratives, case IDs, evidence bytes, private legal
correspondence or credentials.

## Editing and AI

Every generated document remains editable before use. AI is an optional refinement
step, not the canonical source of a format. Deterministic template selection runs first.
A citizen's issue or pasted draft is sent to a remote provider only following an explicit
remote-processing action, a valid identity/capability check, and the shared AI gateway's
exact provider/field/purpose policy.

Model output is untrusted: validate its schema and bounds; keep citizen-supplied facts,
records, jurisdiction, dates, evidence references and legal citations separate; do not
let the model invent authorities, statutes, deadlines, evidence, acknowledgements or
legal effects. On a provider error or invalid response, preserve the local preview rather
than treating generated text as verified. No preview is submitted or emailed by Janavani.

## Saving a reusable format from a citizen draft

Do not store a copy of user prose and then rely on regex redaction. If custom formats
are added, the citizen must explicitly choose “save as a reusable format”; the
application must extract only allow-listed structure (section order, labels, field
requirements, document type, language and declared jurisdiction scope). Reject any
candidate containing values in fields intended for personal/case content. Store it as
a proposed version, with explicit review/moderation before it becomes a shared catalogue
item. Store no source document or evidence with that structural model.

The six curated catalogue entries are reusable source-controlled models. A user-saving
workflow is a future capability and must not be represented as implemented yet.

## Correction learning

Never silently promote a user correction to a trusted global fact. For public authority
metadata, useful corrections may improve the directory only after authoritative
verification and review. For private case content, learning signals must remain
purpose-limited and must not be used for AI training or external profiling by default.

## Verification and output

Where factual or legal references are included, require authoritative sources and
freshness checks appropriate to the jurisdiction. An output can be downloaded or printed
for citizen review; generation is not submission, email delivery, legal advice or proof
of legal effect.
