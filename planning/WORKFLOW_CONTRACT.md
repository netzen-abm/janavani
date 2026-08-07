# Janavani Workflow Contract (MVP v0.1)

## Purpose

Defines the standard workflow for all citizen interactions.

The Conversation Engine executes workflow steps.

Workflow steps never generate documents directly.

---

## Complaint Workflow

START

↓

Issue

↓

Document Type

↓

District

↓

Office Search

↓

Office Selection

↓

Preview

↓

Identity Selection

↓

Document Generation

↓

PDF Generation

↓

Finish

---

## RTI Workflow

START

↓

Issue

↓

Document Type

↓

District

↓

Preview

↓

Identity Selection

↓

Document Generation

↓

PDF Generation

↓

Finish

---

## Engineering Rules

- Every workflow is state-driven.
- Every state has exactly one handler.
- Every handler owns only one responsibility.
- Workflow steps never bypass the Conversation Engine.
- Document generation occurs only after Preview confirmation.
- Privacy rules are applied before document generation.

---

## Used By

- Conversation Engine
- State Registry
- Workflow Engine