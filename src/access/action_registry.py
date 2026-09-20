"""Canonical action registry for Janavani capability authorization.

This registry is a semantic contract, not a second authorization engine.
It records action/capability/resource semantics already present in active
capability code so application authorization, execution contexts, audit,
and future PostgreSQL/RLS mappings can converge on the same vocabulary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResourceType(str, Enum):
    CASE = "case"
    EVIDENCE = "evidence"
    DOCUMENT = "document"
    CONSENT = "consent"
    SUBMISSION = "submission"
    SOS = "sos"


class MutationClass(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"


@dataclass(frozen=True)
class ActionSpec:
    capability_id: str
    action: str
    resource: ResourceType
    mutation: MutationClass
    owner_required: bool
    delegation_supported: bool
    consent_required: bool = False
    approval_required: bool = False
    audit_required: bool = True


# Only actions observed in active capability implementations are registered.
# Future actions must be added from code evidence, not by prediction.
ACTION_REGISTRY: tuple[ActionSpec, ...] = (
    ActionSpec("JNV-CIVIC-COMPLAINT", "create", ResourceType.CASE, MutationClass.CREATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "save", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:add_evidence", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:add_document", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:start_review", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:mark_ready", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:begin_submission", ResourceType.CASE, MutationClass.UPDATE, True, False, True, True),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:queue_submission", ResourceType.CASE, MutationClass.UPDATE, True, False, True, True),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:submit", ResourceType.CASE, MutationClass.EXTERNAL_SIDE_EFFECT, True, False, True, True),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:acknowledge", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:verify_resolution", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("JNV-CIVIC-COMPLAINT", "case:reopen_resolution", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("case:evidence", "evidence:register", ResourceType.EVIDENCE, MutationClass.CREATE, False, False),
    ActionSpec("case:evidence", "evidence:attach", ResourceType.CASE, MutationClass.UPDATE, True, False),
    ActionSpec("case:evidence", "evidence:read", ResourceType.EVIDENCE, MutationClass.READ, True, False),
    ActionSpec("case:consent", "case:consent", ResourceType.CONSENT, MutationClass.UPDATE, True, False),
    ActionSpec("case:submit", "case:begin_submission", ResourceType.SUBMISSION, MutationClass.CREATE, True, False, True, True),
    ActionSpec("case:submit", "case:submit", ResourceType.SUBMISSION, MutationClass.EXTERNAL_SIDE_EFFECT, True, False, True, True),
    ActionSpec("case:submit", "case:acknowledge", ResourceType.SUBMISSION, MutationClass.UPDATE, True, False),
    ActionSpec("case:submit", "case:reconcile_submission", ResourceType.SUBMISSION, MutationClass.UPDATE, True, False),
    ActionSpec("document:review", "document:read", ResourceType.DOCUMENT, MutationClass.READ, True, False),
    ActionSpec("document:review", "document:edit", ResourceType.DOCUMENT, MutationClass.UPDATE, True, False),
    ActionSpec("document:review", "edit", ResourceType.DOCUMENT, MutationClass.UPDATE, True, False),
    ActionSpec("sos:trigger", "sos:trigger", ResourceType.SOS, MutationClass.EXTERNAL_SIDE_EFFECT, True, False, False, True),
)

# Semantic aliases observed in active tests are intentionally not registered
# as separate actions. For example, "submit" is a legacy execution-context
# spelling; the canonical active capability action is "case:submit".


def get_action_spec(capability_id: str, action: str) -> ActionSpec | None:
    for spec in ACTION_REGISTRY:
        if spec.capability_id == capability_id and spec.action == action:
            return spec
    return None


def require_action_spec(capability_id: str, action: str) -> ActionSpec:
    spec = get_action_spec(capability_id, action)
    if spec is None:
        raise ValueError(f"Unregistered capability action: {capability_id}:{action}")
    return spec


def registered_actions() -> tuple[ActionSpec, ...]:
    return ACTION_REGISTRY
