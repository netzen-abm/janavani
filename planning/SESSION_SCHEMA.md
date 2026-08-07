# Janavani Session Schema (MVP v0.1)

## Purpose

Defines the standard structure of the conversation session.

Every workflow step MUST read and write using this schema.

---

## Session Object

```python
{
    # Workflow
    "workflow": "Complaint",

    # Citizen Issue
    "issue": "",

    # Document Type
    "document": "",

    # Location
    "district": "",
    "department": "",

    # Office Search Results
    "offices": [],

    # Selected Office
    "office": {
        "office_id": "",
        "office_name": "",
        "office_address": "",
        "department": "",
        "district": ""
    },

    # Identity
    "identity_mode": "anonymous",

    # Citizen Details
    "name": "",
    "address": "",
    "phone": "",
    "email": "",

    # Evidence
    "photo": None
}
```

---

## Rules

- Every workflow step updates only its own fields.
- Unknown keys should never be created dynamically.
- Identity defaults to `anonymous`.
- `office` follows the Office Schema.
- `offices` contains a list of Office Schema objects.

---

## Used By

- Conversation Engine
- Preview Step
- Generate Step
- Document Engine