# Janavani Privacy Contract (MVP v0.1)

## Principle

Privacy is enabled by default.

Citizens should disclose only the minimum information required.

---

# Identity Modes

## Anonymous (Default)

Citizen name is omitted.

Citizen address is omitted.

Citizen phone is omitted.

Citizen email is omitted.

Signature:

Concerned Citizen

---

## Name Only

Include:

- Name

Exclude:

- Address
- Phone
- Email

---

## Full Identity

Include:

- Name
- Address
- Phone
- Email

---

# Engineering Rules

- Identity mode defaults to `anonymous`.
- Builders must respect the selected identity mode.
- Builders never expose hidden personal data.
- Preview screen must clearly display the selected identity mode.
- Citizens may change identity mode before document generation.

---

# Privacy by Design

The system must always:

- Minimize personal data.
- Collect only what is necessary.
- Avoid unnecessary storage.
- Separate identity from complaint content where possible.
- Support anonymous civic participation.

---

# Used By

- Conversation Engine
- Preview Step
- Complaint Builder
- RTI Builder
- Petition Builder