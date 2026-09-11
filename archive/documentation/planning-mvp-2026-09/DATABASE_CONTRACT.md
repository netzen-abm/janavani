# Archived: Janavani Database Contract (MVP v0.1)

> **ARCHIVED / HISTORICAL** — preserved verbatim from `planning/DATABASE_CONTRACT.md` during the 2026-09 documentation convergence pass.
>
> Current architecture and data-boundary decisions live in the canonical documentation chain, especially `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE_DATA_BOUNDARY.md`, and `docs/JANAVANI_MASTER_ARCHITECTURE.md`.

---

# Janavani Database Contract (MVP v0.1)

## Purpose

Defines the database responsibilities and data ownership.

The database stores data only.

Business logic belongs in services.

---

# Offices Table

Required Fields

```python
office_id
office_name
office_address
department
district
```

Optional Fields

```python
email
phone
website
latitude
longitude
pincode
officer_name
officer_designation
```

---

# Citizens

MVP

No permanent storage.

Identity is temporary.

---

# Complaints

Future

- complaint_id
- office_id
- issue
- created_at
- status

---

# Ratings

rating_id

office_id

score

comment

created_at

---

# Engineering Rules

Database

✓ stores data

Database

✗ contains no business logic

✗ knows nothing about Telegram

✗ knows nothing about workflows

---

# Ownership

Conversation Engine

↓

Services

↓

Repositories

↓

Database
