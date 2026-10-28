# Document Template and Correction System

## Current implementation

The active versioned source catalogue is `src/documents/template_catalogue.py`.
It currently provides complaint, grievance, RTI, representation and petition
formats. `src/services/civic_draft_workflow.py` composes the same deterministic
preview for WebApp and Telegram and may request optional, consent-gated AI wording
improvements. The AI response is accepted only through a bounded output schema.

The catalogue is curated and source-controlled in this phase. Persistent user-saved
custom formats, shared promotion of user formats, and model-training from edits are
not implemented. The four empty legacy document modules are not alternate drafting
engines; preserve and inspect them before any cleanup decision.

## Template contract

Every template should declare purpose, document type, jurisdiction scope, language,
version, required and optional fields, ordered sections, provenance and review status.
A template is a reusable structure, not an immutable legal form. Complaint/grievance
requests and RTI requests for existing records remain distinct flows.

The structural model may contain labels and allow-listed section identifiers. It
must not contain citizen names, postal addresses, contact details, account identifiers,
raw narratives, case IDs, evidence bytes, private legal correspondence or credentials.

## Editing and AI

Every generated document remains editable before use. AI is an optional refinement
step, not the canonical source of the format. Deterministic template selection runs
first. A citizen's issue or pasted draft is sent to a remote provider only following
an explicit remote-processing action, a valid identity/capability check, and the
shared AI gateway's exact provider/field/purpose policy.

Model output is untrusted: validate its schema and bounds; keep user-supplied records,
jurisdiction, dates, evidence references and legal citations separate; do not let the
model invent authorities, statutes, deadlines, evidence, acknowledgements or legal
effects. On a provider error or invalid response, preserve the local preview rather
than treating generated text as verified. No draft is submitted or emailed by this
preview capability.

## Saving a reusable format from a citizen draft

Do not store a copy of user prose and then rely on regex redaction. If custom formats
are added, the citizen must explicitly choose “save as a reusable format”; the
application must extract only allow-listed structure (section order, labels, field
requirements, document type, language and declared jurisdiction scope). Reject any
candidate containing values in fields intended for personal/case content. Store it
as a proposed version, with explicit review/moderation before it becomes a shared
catalogue item. Store no source document or evidence with that structural model.

The current static catalogue is the durable reusable source for the supported
standard formats; custom persisted format management is a future capability and
must not be represented as implemented yet.

## Correction learning

Never silently promote a user correction to a trusted global fact. For public
authority metadata, useful corrections may improve the directory only after
authoritative verification and review. For private case content, learning signals
must remain purpose-limited and must not be used for AI training or external
profiling by default.

## Verification and output

Where factual or legal references are included, require authoritative sources and
freshness checks appropriate to the jurisdiction. An output can be downloaded or
printed for citizen review; document generation is not submission, email delivery or
proof of legal effect.
