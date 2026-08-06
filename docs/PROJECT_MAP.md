# Janavani Project Map

Version: 1.0

This document is the single source of truth for the repository.

---

# Mission

Janavani is a Privacy-First Citizen Governance Platform.

Its purpose is to help every citizen exercise constitutional rights through secure, privacy-preserving, legally-informed digital workflows.

---

# Engineering Principles

1. Privacy at the Core
2. Security by Default
3. Open Source First
4. Offline First whenever possible
5. End-to-End Encryption
6. User Owns Their Data
7. Modular Architecture
8. Replaceability over Coupling
9. Testability over Convenience
10. Human-Centered Design

---

# Repository Layout

Root
│
├── src/
│
├── docs/
│
├── planning/
│
├── database/
│
├── scripts/
│
├── archive/
│
├── api/
│
└── services/

```

# Active Source Code

Everything inside

src/

is production code.

No production logic should exist outside src.

---

# src/

Contains the application.

Subdirectories

conversation/
workflow/
engine/
documents/
domain/
services/
storage/
database/

form the Core Platform.

---

# docs/

Architecture documentation

Engineering decisions

Repository rules

Developer onboarding

---

# planning/

Vision

Research

Founder Constitution

Architecture ideas

Future planning

No executable code.

---

# archive/

Deprecated code.

Never imported.

Never executed.

Reference only.

---

# database/

Static datasets.

CSV

JSON

Seed files

No business logic.

---

# api/

External APIs

Adapters

Future REST endpoints

---

# scripts/

Development utilities

Installation

Migration

Automation

Never imported by production.

# Application Entry Point

Current Production Entry

src/main.py

All future platform startup should originate here.

---

# Workflow Architecture

Workflow Engine

↓

Workflow Registry

↓

Workflow Context

↓

Workflow Step

↓

Document Builder

↓

Delivery

Each workflow step must implement

WorkflowStep

No workflow should bypass the engine.

---

# Conversation Flow

Telegram

↓

Conversation Engine

↓

Workflow Engine

↓

Workflow Step

↓

Workflow Context

↓

Documents

↓

Delivery

---

# Document Flow

Issue

↓

Classification

↓

Office Selection

↓

Evidence

↓

Identity

↓

Complaint Builder

↓

Document Standards

↓

PDF Generator

↓

Delivery

---

# AI Flow

Citizen Request

↓

Legal Brain

↓

Classification

↓

Document Builder

↓

Human Review

↓

Output

# Ownership Rules

conversation/

Owns conversations only.

engine/

Owns orchestration only.

workflow/

Owns workflow logic only.

documents/

Owns document creation only.

services/

Owns integrations only.

storage/

Owns persistence only.

domain/

Owns business models only.

No cross-responsibility allowed.

# Future Modules

Identity

Evidence

RTI

Petition

Appeal

Email Delivery

Digital Signature

Audit Trail

Citizen Vault

Consent Manager

Notification Engine

Knowledge Graph

AI Legal Assistant

Open Government APIs

---

# Engineering Rule

Whenever a new file is added,

the Project Map must be updated.

This document is the architectural constitution of Janavani.


