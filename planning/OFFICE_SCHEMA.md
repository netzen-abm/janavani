# Janavani Office Schema (MVP v0.1)

## Purpose

Defines the standard structure of every government office used throughout Janavani.

Every service returning an office MUST follow this schema.

---

## Required Fields

```python
{
    "office_id": "",
    "office_name": "",
    "office_address": "",
    "department": "",
    "district": ""
}
```

---

## Optional Fields

```python
{
    "email": "",
    "phone": "",
    "website": "",
    "latitude": "",
    "longitude": "",
    "pincode": "",
    "officer_name": "",
    "officer_designation": ""
}
```

---

## Rules

- Every office must have a unique `office_id`.
- `office_name` is the official department name.
- `office_address` must contain the postal address.
- `department` is used for search.
- `district` is used for filtering.

---

## Used By

- Office Service
- Conversation Engine
- Complaint Builder
- RTI Builder
- Petition Builder
- PDF Generator