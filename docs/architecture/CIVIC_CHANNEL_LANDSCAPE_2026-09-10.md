# Civic Channel Landscape and Janavani Position — 2026-09-10

## Purpose

Record verified external civic-reporting channels relevant to Janavani's provider-neutral civic-action architecture. External services are reference channels and must not become Janavani's domain authority.

## Bengaluru

### Sahaaya 2.0

The Greater Bengaluru Authority currently exposes **SAHAAYA 2.0 (Public Grievance)** as an e-service. The current GBA site also reflects the five-city-corporation structure. The official BBMP/GBA app listing describes Sahaaya 2.0 as a unified application for registering grievances against multiple departments and tracking them.

Current public reporting indicates that Sahaaya 2.0 spans 31 departments/urban service agencies through 34 channels, including app, helpline and WhatsApp. A September 2026 GBA consultation is explicitly developing Sahaaya 3.0, so claims about future functionality must be treated as planned rather than production functionality.

### Fix Pothole / ರಸ್ತೆ ಗುಂಡಿ ಗಮನ

The official BBMP Fix Pothole app remains a distinct road-maintenance channel. Its current Android listing documents photo-based, geotagged reporting, automatic ward routing, official dashboards, transfer between departments/wards, and field updates with GPS/photos. The current GBA/BBMP web presence still links to Fix Pothole.

### Verified contact fallback

The official BBMP control-room document lists 1533 as the 24/7 toll-free helpline, 080-22660000 as a head-office control-room number, and 9480685700 as the head-office WhatsApp number. These are safer canonical references for Janavani research than an unverified pothole-specific WhatsApp number.

## National channels

### Rajmargyatra

NHAI's current official app listing describes Rajmargyatra as its all-in-one highway app, including complaint registration/tracking for road conditions, toll operations and facilities, plus direct 1033 emergency support. It is the appropriate national-highway channel; it should not be treated as a general municipal grievance platform.

### Meri Sadak

The current official app listing describes Meri Sadak as the Government's citizen-feedback/grievance channel for PMGSY and other covered rural roads. It supports photographs, tracking, official contact details and reopening of complaints within the documented period. It is therefore a rural-road channel rather than a substitute for Bengaluru municipal reporting.

### CPGRAMS

CPGRAMS is the Government of India's centralized public grievance platform. Its current portal states that it is connected to Ministries/Departments and States, provides tracking, feedback and appeal, and is available through web/mobile/UMANG. It is an escalation/government-grievance channel, not a universal replacement for the responsible local agency.

## Janavani architectural conclusion

Janavani should **not duplicate these systems as isolated mini-apps**. It should provide a canonical civic-action layer that can:

1. identify the responsible jurisdiction/authority;
2. collect a canonical Case and evidence package once;
3. preserve provenance, hashes, timestamps and user approvals;
4. select an appropriate delivery adapter/channel;
5. submit only through an explicit, provider-specific adapter;
6. persist transport outcome separately from acknowledgement;
7. require independent evidence before marking a case ACKNOWLEDGED;
8. support follow-up/escalation when the external channel closes or fails to resolve the matter;
9. preserve the citizen's evidence and case history independently of any external portal.

The key differentiator is therefore **not another grievance form**. It is a provider-neutral civic action and accountability layer that can operate across government channels while preserving one citizen-controlled case history.

## Pothole / infrastructure intelligence opportunity

Recent Bengaluru work demonstrates two complementary patterns:

- Citizen/vehicle sensing: dashcam + GPS + accelerometer + computer vision can detect road defects and associate them with road contracts/contractors.
- Civic road assessment: Bengaluru East has used camera surveys, YOLO-based defect detection and a Vision Language Model to estimate pothole dimensions and support repair-material/cost planning.

These should inform Janavani's optional **Evidence Intelligence / Infrastructure Observation** capability, but AI output must remain an observation or recommendation until verified. Contract-to-responsibility mapping should be provenance-backed and should never automatically accuse a contractor or official based only on model inference.

## Research caution

The frequently repeated claim that Sahaaya has "over 7.81 lakh" grievances is a dated news snapshot and should not be treated as a current live count. September 2026 reporting gives category figures whose combined total is materially different. Janavani documentation should always attach a date/source to external statistics.

Likewise, the reported Bengaluru engineer system searching approximately 2,900 contracts is a reported demonstration, not evidence of an official government integration. Janavani may study the pattern but should not represent it as a government capability.
