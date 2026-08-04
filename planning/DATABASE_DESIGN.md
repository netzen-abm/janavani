# 🇮🇳 JANAVANI
# DATABASE DESIGN
Version 1.0

---

# Purpose

This document defines the database architecture of Janavani.

The database should support:

• Telegram Bot
• Future Website
• Android App
• WhatsApp
• APIs

without redesign.

---

# Database Philosophy

The database stores facts.

Business logic belongs in Python.

AI belongs in Services.

Conversation belongs in the Conversation Engine.

The database never contains workflow logic.

---

# Database

Supabase (PostgreSQL)

---

# Core Tables

1. citizens

2. issues

3. evidence

4. locations

5. departments

6. offices

7. documents

8. submissions

9. conversations

10. volunteers

---

# Relationships

Citizen

↓

creates

↓

Issue

↓

has

↓

Evidence

↓

belongs to

↓

Location

↓

handled by

↓

Department

↓

assigned to

↓

Office

↓

creates

↓

Document

↓

submitted as

↓

Submission

---

# Design Rules

Every table should have:

id

created_at

updated_at

status

Every relationship should use IDs.

No duplicated information.

Normalize wherever practical.

---

# Future Expansion

The database must support:

Voice

Photos

GPS

Multiple Languages

Multiple Documents

Government APIs

Volunteer Verification

Office Ratings

without redesign.

---

# Guiding Principle

Design once.

Scale forever.
