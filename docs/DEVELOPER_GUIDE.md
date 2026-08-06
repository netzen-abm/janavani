# Janavani Developer Guide

Version: 1.0

---

# Welcome

Welcome to Janavani.

Janavani is a Privacy-First Citizen Governance Platform.

Before writing code, understand the mission:

> Build software that helps citizens exercise constitutional rights safely, privately, and simply.

Every engineering decision should increase:

• Trust
• Privacy
• Security
• Reliability
• Simplicity

---

# Read These Documents First

Every engineer should read these documents in order:

1. README.md
2. PROJECT_MAP.md
3. ENGINEERING_CONSTITUTION.md
4. SYSTEM_QUALITY_STANDARD.md
5. ARCHITECTURE.md
6. WORKFLOWS.md

Only after understanding these should development begin.

---

# Repository Structure

Root/

docs/

planning/

src/

archive/

database/

scripts/

.github/

Only production code belongs inside src/.

---

# Production Code

src/

contains:

app/

conversation/

workflow/

engine/

documents/

services/

domain/

storage/

database/

utils/

adapters/

Every module has one responsibility.

No business logic belongs outside src/.

---

# Workflow Architecture

Citizen Request

↓

Conversation Engine

↓

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

Never bypass this flow.

---

# Document Pipeline

Issue

↓

Classification

↓

Office Search

↓

Evidence

↓

Identity

↓

Complaint Builder

↓

PDF Generator

↓

Delivery

All document types follow this pipeline.

---

# Coding Standards

Prefer composition.

Avoid duplication.

Write readable code.

Use descriptive names.

Keep functions small.

Document public APIs.

Never hardcode secrets.

Never bypass architecture.

---

# Git Workflow

Before committing:

Compile

Review

Update documentation

Run tests

Verify architecture

Then:

git add

git commit

git push

---

# If You Need a New Feature

Before creating a new file ask:

Does a similar module already exist?

Can I extend an existing module?

Does this belong inside the current architecture?

If the answer is unclear,

update PROJECT_MAP.md first.

---

# Engineering Principle

Every pull request should make the repository:

Simpler

Safer

More maintainable

Better documented

Never more complicated.

