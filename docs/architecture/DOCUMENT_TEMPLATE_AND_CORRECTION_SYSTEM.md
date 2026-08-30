# Document Template and Correction System

## Template library

Janavani should maintain versioned canonical pre-draft templates for common civic actions, including complaint, grievance, RTI, petition, objection, representation, request/application, reminder/follow-up, and escalation where legally and operationally appropriate.

Templates are reference starting points, not immutable legal forms. Each template must declare purpose, required fields, optional fields, jurisdictional scope, language variants, version, provenance, and review status.

## Structured template model

```text
Template
 ├── purpose
 ├── document_type
 ├── jurisdiction
 ├── required_fields
 ├── optional_fields
 ├── To block
 ├── CC block
 ├── body sections
 ├── evidence references
 ├── language variants
 ├── version
 └── provenance/review status
```

## Editing

The generated draft must remain editable before final export. Editing must support both document content and recipient fields. The user must be able to see which recipient details came from verified sources and which details are user-provided or unverified.

## Correction learning

Never silently promote a user correction to a trusted global fact.

```text
User correction
      ↓
Current document updated for user
      ↓
Structured correction event
      ↓
Privacy minimization
      ↓
Verification queue
      ↓
Corroboration / authoritative source check
      ↓
Trusted directory update (only if verified)
```

For public authority metadata, useful corrections may improve the authority directory after verification. For private case content, learning signals must remain purpose-limited and must not be used for AI training or external profiling by default.

## Verification methods

Use multiple verification classes as appropriate:

1. authoritative government source;
2. second independent authoritative source;
3. current official communication or directory;
4. controlled human review for unresolved conflicts;
5. source freshness check.

A user correction alone is a signal, not verification.

## Document output

Final generation produces a downloadable/printable PDF and, where supported, an editable document such as DOCX. Email delivery is outside this capability.
