# 🇮🇳 JANAVANI
# WORKFLOWS
Version 1.0

---

# Workflow 1

Citizen Complaint Workflow

---

## Goal

Transform a citizen's government-related problem into a professionally drafted complaint addressed to the correct government office.

---

# Start

Citizen opens Telegram.

Citizen starts chatting.

Citizen describes the problem naturally.

Example:

"My ration card has been pending for three months."

or

"There is a broken water pipe near my house."

or

"The Panchayat has not collected garbage."

Janavani never asks the citizen to choose a department first.

The conversation always starts with the problem.

---

# Step 1

Capture the Issue

Citizen writes:

"My road has been damaged for six months."

System stores:

Issue Description

Conversation State → ISSUE_CAPTURED

---

# Step 2

Offer Document Types

Janavani replies:

What would you like to generate?

1. Complaint

2. Grievance

3. Grievance Petition

4. RTI Application

5. Representation Letter

Citizen selects one option.

System stores:

Document Type

Conversation State → DOCUMENT_SELECTED

---

# Step 3

Collect Location

Ask only the missing information.

District

↓

Local Body

↓

Ward (optional)

↓

Village (optional)

↓

Landmark (optional)

System stores location details.

Conversation State → LOCATION_CAPTURED

---

# Step 4

Identify Department

Based on:

Issue

+

Location

Determine the most appropriate department.

Example:

Broken road

↓

PWD

or

Panchayat

or

Municipality

---

# Step 5

Find Office

Search the office database.

Return:

Office Name

Address

Phone

Email

Officer (if available)

Conversation State → OFFICE_IDENTIFIED

---

# Step 6

Collect Citizen Details

Ask only if missing.

Citizen Name

Address

Phone (optional)

Email (optional)

Conversation State → CITIZEN_CAPTURED

---

# Step 7

Generate Complaint

Build a structured complaint using:

Citizen Details

Issue

Department

Office

Location

Date

Conversation State → DOCUMENT_GENERATED

---

# Step 8

Generate PDF

Produce a clean PDF.

Include:

Heading

Recipient

Subject

Complaint

Citizen Details

Signature Area

Conversation State → PDF_GENERATED

---

# Step 9

Delivery

Send PDF to citizen.

Provide office information.

Example:

Office:

Assistant Engineer

PWD Roads Division

Ernakulam

Email:

example@gov.in

Phone:

xxxxxxxxxx

Conversation State → COMPLETED

---

# End Result

Citizen receives:

✔ Complaint PDF

✔ Correct Office

✔ Contact Details

✔ Submission Guidance

The conversation ends successfully.
