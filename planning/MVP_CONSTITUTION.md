# Janavani MVP Constitution (v0.1)

## Purpose

This document defines the immutable engineering principles of the Janavani MVP.

Every contributor, AI assistant, and developer must follow these principles before changing the codebase.

---

# 1. Privacy by Design

Privacy is enabled by default.

Anonymous participation is the default.

Identity disclosure is optional.

Only the minimum personal information necessary may be collected.

---

# 2. Separation of Responsibilities

Conversation Engine

↓

Workflow

↓

Services

↓

Document Engine

↓

Builders

↓

PDF Generator

↓

Repositories

↓

Database

Every layer has one responsibility.

---

# 3. Engineering Contracts

The following contracts are authoritative.

- OFFICE_SCHEMA.md
- SESSION_SCHEMA.md
- DOCUMENT_CONTRACT.md
- PRIVACY_CONTRACT.md
- WORKFLOW_CONTRACT.md
- SERVICE_CONTRACT.md

Implementation must follow these contracts.

---

# 4. Workflow First

Conversation state drives the application.

No workflow step may bypass the Conversation Engine.

---

# 5. Builders

Builders create text only.

Builders never:

- call Telegram
- generate PDFs
- access databases

---

# 6. Services

Services contain business logic.

Services never own conversation state.

Services never access Telegram.

---

# 7. PDF Generation

PDF generation is a rendering concern only.

Rendering must never change document content.

---

# 8. Repository Standards

One responsibility per module.

No duplicate implementations.

No business logic in UI.

No UI in services.

No database access in builders.

---

# 9. Documentation First

Architecture changes require updating contracts before implementation.

---

# 10. MVP Goal

Produce legally structured citizen documents with:

- Privacy
- Simplicity
- Maintainability
- Extensibility