# Archived: Janavani Platform Service Contract (MVP-era)

> **ARCHIVED / HISTORICAL** — preserved from `planning/SERVICE_CONTRACT.md` during the 2026-09 documentation convergence pass.
>
> The service boundaries below are historical MVP guidance. Current shared capability, application, domain, workflow, adapter and provider boundaries are governed by the active architecture and capability contracts.

---

# Janavani Platform Service Contract (MVP v0.1)

## Purpose

Defines the responsibilities of every service in Janavani.

Services contain business logic.

Services never communicate directly with Telegram.

Services never generate PDFs.

Services never manage conversation state.

---

# Office Service

Responsibilities

- Search offices
- Filter offices
- Return Office Schema objects

---

# Document Service

Responsibilities

- Coordinate document generation
- Call Document Engine
- Return document text

---

# Complaint Service

Responsibilities

- Complaint-specific business rules
- Complaint validation
- Complaint workflows

---

# Search Service

Responsibilities

- Search government directory
- Search departments
- Search offices

---

# Language Service

Responsibilities

- Translation
- Localization
- Language selection

---

# AI Service

Responsibilities

- Issue classification
- Future legal assistance
- Future summarization

---

# Privacy Service

Responsibilities

- Identity filtering
- Data minimization
- Privacy enforcement

---

# Engineering Rules

Services

✓ contain business logic

Services

✗ never call Telegram

✗ never generate PDFs

✗ never access UI

✗ never own workflow state

---

## Architecture

Telegram

↓

Conversation Engine

↓

Workflow

↓

Services

↓

Repositories

↓

Database
