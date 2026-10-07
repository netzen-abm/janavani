"""Canonical civic case enums and status vocabulary."""
from enum import Enum

class CaseType(str, Enum):
    Complaint = "complaint"
    Grievance = "grievance"
    Rti = "rti"
    Petition = "petition"
    Representation = "representation"
    Objection = "objection"
    Appeal = "appeal"
    Corruption = "corruption"
    Misbehaviour = "misbehaviour"
    TransferConcern = "transfer_concern"
    Other = "other"

class CaseStatus(str, Enum):
    Draft = "draft"
    Review = "review"
    Ready = "ready"
    Submitting = "submitting"
    Queued = "queued"
    Submitted = "submitted"
    Acknowledged = "acknowledged"
    FollowUp = "follow_up"
    InProgress = "in_progress"
    Responded = "responded"
    Resolved = "resolved"
    Escalated = "escalated"
    Closed = "closed"
    Archived = "archived"

class CaseEventType(str, Enum):
    Created = "created"
    Edited = "edited"
    ReviewStarted = "review_started"
    Approved = "approved"
    EvidenceAdded = "evidence_added"
    DocumentAdded = "document_added"
    Submitting = "submitting"
    Queued = "queued"
    Submitted = "submitted"
    Acknowledged = "acknowledged"
    FollowUp = "follow_up"
    Response = "response"
    Resolved = "resolved"
    Escalated = "escalated"
    Correction = "correction"
    CitizenVerified = "citizen_verified"
    CitizenReopened = "citizen_reopened"
    Closed = "closed"
    Archived = "archived"

# Python-facing aliases retained for existing application code; iteration and
# serialization use the canonical Rust-compatible member names above.
for _name, _canonical in {
    "COMPLAINT":"Complaint","GRIEVANCE":"Grievance","RTI":"Rti","PETITION":"Petition",
    "REPRESENTATION":"Representation","OBJECTION":"Objection","APPEAL":"Appeal","CORRUPTION":"Corruption",
    "MISBEHAVIOUR":"Misbehaviour","TRANSFER_CONCERN":"TransferConcern","OTHER":"Other",
}.items(): setattr(CaseType, _name, getattr(CaseType, _canonical))
for _name, _canonical in {
    "DRAFT":"Draft","REVIEW":"Review","READY":"Ready","SUBMITTING":"Submitting","QUEUED":"Queued",
    "SUBMITTED":"Submitted","ACKNOWLEDGED":"Acknowledged","FOLLOW_UP":"FollowUp","IN_PROGRESS":"InProgress",
    "RESPONDED":"Responded","RESOLVED":"Resolved","ESCALATED":"Escalated","CLOSED":"Closed","ARCHIVED":"Archived",
}.items(): setattr(CaseStatus, _name, getattr(CaseStatus, _canonical))
for _name, _canonical in {
    "CREATED":"Created","EDITED":"Edited","REVIEW_STARTED":"ReviewStarted","APPROVED":"Approved",
    "EVIDENCE_ADDED":"EvidenceAdded","DOCUMENT_ADDED":"DocumentAdded","SUBMITTING":"Submitting","QUEUED":"Queued",
    "SUBMITTED":"Submitted","ACKNOWLEDGED":"Acknowledged","FOLLOW_UP":"FollowUp","RESPONSE":"Response",
    "RESOLVED":"Resolved","ESCALATED":"Escalated","CORRECTION":"Correction","CITIZEN_VERIFIED":"CitizenVerified",
    "CITIZEN_REOPENED":"CitizenReopened","CLOSED":"Closed","ARCHIVED":"Archived",
}.items(): setattr(CaseEventType, _name, getattr(CaseEventType, _canonical))

CITIZEN_VERIFIED_EVENT = CaseEventType.CitizenVerified
CITIZEN_REOPENED_EVENT = CaseEventType.CitizenReopened
