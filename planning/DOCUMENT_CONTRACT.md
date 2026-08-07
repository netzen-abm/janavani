# Janavani Document Contract (MVP v0.1)

## Purpose

Defines the interface between the Conversation Engine and the Document Engine.

The Conversation Engine never generates documents.

The Document Engine never manages conversations.

Both communicate only through this contract.

---

## Supported Document Types

- Complaint
- RTI
- Petition
- Grievance

---

## Complaint Builder Input

```python
{
    "issue": "",
    "office_name": "",
    "office_address": "",
    "identity_mode": "anonymous",

    "citizen": {

        "name": "",
        "address": "",
        "phone": "",
        "email": ""

    }

}
```

---

## Complaint Builder Output

Plain UTF-8 text.

Example:

```
To

The Officer In Charge

Village Office

...

Subject

Complaint regarding...

...

Yours faithfully,

Concerned Citizen
```

---

## PDF Generator Input

Plain text

---

## PDF Generator Output

PDF file

---

## Rules

- Builders never generate PDFs.
- Builders never call Telegram.
- Builders never access databases.
- Builders only return formatted document text.
- PDF generation is handled separately.

---

## Architecture

Conversation

↓

Document Engine

↓

Complaint Builder

↓

Document Text

↓

PDF Generator

↓

PDF File