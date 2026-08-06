# Janavani Architecture Constitution

Version: 1.0
Status: LOCKED
Owner: Janavani Core Team

---

# Mission

Build the world's most trusted Citizen Governance Platform.

Janavani exists to transform citizen problems into effective government action while preserving privacy, security, dignity, transparency, and simplicity.

---

# Core Philosophy

Citizen First

Privacy at the Core

Security at the Core

Open Source First

Simple Systems

Replaceable Components

Domain-Driven Design

Workflow-Driven Architecture

Long-Term Thinking

---

# First Principle

Citizens should describe their problem.

Janavani discovers everything else.

The citizen should never need to understand:

- Government hierarchy
- Departments
- Offices
- Legal procedures
- Forms
- Bureaucracy

Janavani carries that complexity.

---

# Architectural Layers

Citizen

↓

Interfaces

- Telegram
- Web
- WhatsApp
- Mobile
- API

↓

Workflow Engine

↓

Domain Layer

↓

Services

↓

Storage

---

# Dependency Rule

Dependencies flow only downward.

Interfaces

↓

Workflow

↓

Domain

↓

Services

↓

Storage

Never upward.

---

# Folder Responsibilities

## adapters/

Interface adapters only.

Responsible for communication with external platforms.

No business logic.

---

## workflow/

Citizen workflows.

Examples:

Complaint

RTI

Petition

Appeal

Passport

Pension

---

## engine/

Workflow execution.

State registry.

Workflow registry.

Routing.

Never contains business rules.

---

## domain/

Core governance concepts.

Citizen

Issue

Office

Document

Workflow

Evidence

Pure business logic.

Independent of Telegram or databases.

---

## services/

Application services.

Examples:

Office search

AI

Classification

Notifications

Language

Encryption

---

## documents/

Document builders.

Complaint

RTI

Petition

PDF generation

Formatting

---

## storage/

Persistence.

Supabase

Future PostgreSQL

Future Object Storage

Replaceable through interfaces.

---

# Engineering Principles

## Single Responsibility

Every module has one purpose.

---

## Open / Closed

The system is open for extension.

Closed for modification.

Adding a new workflow should not require changing the engine.

---

## Composition over inheritance

Prefer small reusable components.

---

## Interfaces over implementations

Depend on abstractions.

Never on specific technologies.

---

## Stateless services

Services should avoid storing state whenever possible.

---

## Testability

Every service should be independently testable.

---

# Security at the Core

Security is a property of the architecture.

Not a feature.

Principles:

Default deny

Least privilege

Secure defaults

Secrets never hardcoded

Encrypted communication

Minimal attack surface

Auditability

---

# Privacy at the Core

Privacy is a core architectural property.

Principles:

Anonymous participation whenever legally possible.

Collect minimum information.

Store minimum information.

Delete unnecessary information.

Citizen owns their data.

Identity is optional whenever legally permissible.

No profiling.

No surveillance.

---

# Replaceability Principle

Every technology should be replaceable.

Telegram

↓

Adapter

↓

Workflow Engine

Tomorrow:

Web

↓

Adapter

↓

Workflow Engine

No workflow changes.

No domain changes.

No document changes.

---

# Simplicity Principle

Every feature must make Janavani:

Simpler

More trustworthy

Or more capable.

If it does none of these,

it should not be added.

---

# Long-Term Vision

Janavani is not a chatbot.

Janavani is not a complaint generator.

Janavani is a Citizen Governance Operating System.

Every future decision should strengthen this vision.

---

END
