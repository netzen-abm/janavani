from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.repositories.citizen_document_format import InMemoryCitizenDocumentFormatRepository
from src.storage.provider_composition import PERSISTED_DOMAINS
from src.web import civic_draft_router, citizen_document_formats_router


CAPABILITY = "document:format:manage"


def _context(authorization, request_id=None):
    if authorization not in {"Bearer owner-a", "Bearer owner-b", "Bearer unprivileged"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authenticated identity required")
    owner = authorization.removeprefix("Bearer ")
    capabilities = frozenset({CAPABILITY}) if owner != "unprivileged" else frozenset()
    return IdentityContext(Principal(
        principal_id=owner, identity_mode=IdentityMode.AUTHENTICATED,
        authentication_method=AuthenticationMethod.PASSKEY,
        interface="test", capabilities=capabilities,
    ))


def _client(monkeypatch):
    repository = InMemoryCitizenDocumentFormatRepository()
    monkeypatch.setattr(citizen_document_formats_router, "require_authenticated_identity", _context)
    monkeypatch.setattr(civic_draft_router, "require_authenticated_identity", _context)
    monkeypatch.setattr(citizen_document_formats_router, "create_citizen_document_format_repository", lambda: repository)
    monkeypatch.setattr(civic_draft_router, "create_citizen_document_format_repository", lambda: repository)
    app = FastAPI()
    app.include_router(civic_draft_router.router)
    app.include_router(citizen_document_formats_router.router)
    return TestClient(app), repository


def _save(client, token="owner-a", **overrides):
    payload = {
        "template_id": "complaint.general",
        "template_version": 1,
        "section_field_names": ["issue", "proposal_or_notice"],
        "save_confirmation": True,
    }
    payload.update(overrides)
    return client.post("/civic/drafts/formats", headers={"Authorization": f"Bearer {token}"}, json=payload)


def test_saved_format_persists_only_canonical_structure_and_is_owner_scoped(monkeypatch):
    client, _repository = _client(monkeypatch)
    saved = _save(client)
    assert saved.status_code == 200, saved.text
    item = saved.json()
    assert item["template_id"] == "complaint.general"
    assert item["section_field_names"] == ["issue", "proposal_or_notice"]
    assert "owner_principal_id" not in item
    assert "source_draft" not in item
    assert client.get("/civic/drafts/formats", headers={"Authorization": "Bearer owner-a"}).json()["formats"][0]["format_id"] == item["format_id"]
    assert client.get(f"/civic/drafts/formats/{item['format_id']}", headers={"Authorization": "Bearer owner-b"}).status_code == 404
    assert client.request("DELETE", f"/civic/drafts/formats/{item['format_id']}", headers={"Authorization": "Bearer owner-b"}, json={"delete_confirmation": True}).status_code == 404


def test_save_requires_separate_confirmation_and_rejects_arbitrary_text(monkeypatch):
    client, _repository = _client(monkeypatch)
    assert _save(client, save_confirmation=False).status_code == 400
    response = _save(client, source_draft="NAME: Alice; private account ID 12345")
    assert response.status_code == 422


def test_unknown_or_duplicate_section_ids_are_rejected(monkeypatch):
    client, _repository = _client(monkeypatch)
    assert _save(client, section_field_names=["issue", "Citizen's custom private heading"]).status_code == 422
    assert _save(client, section_field_names=["issue", "issue"]).status_code == 422


def test_missing_capability_is_denied_and_delete_needs_confirmation(monkeypatch):
    client, _repository = _client(monkeypatch)
    assert _save(client, token="unprivileged").status_code == 403
    item = _save(client).json()
    assert client.request("DELETE", f"/civic/drafts/formats/{item['format_id']}", headers={"Authorization": "Bearer owner-a"}, json={"delete_confirmation": False}).status_code == 400
    assert client.request("DELETE", f"/civic/drafts/formats/{item['format_id']}", headers={"Authorization": "Bearer owner-a"}, json={"delete_confirmation": True}).json()["deleted"] is True


def test_duplicate_structure_is_idempotent_within_an_owner(monkeypatch):
    client, _repository = _client(monkeypatch)
    first = _save(client).json()
    second = _save(client).json()
    assert first["format_id"] == second["format_id"]
    other_owner = _save(client, token="owner-b").json()
    assert other_owner["format_id"] != first["format_id"]


def test_saved_format_preview_uses_server_record_not_client_template(monkeypatch):
    client, _repository = _client(monkeypatch)
    saved = _save(client, section_field_names=["issue"]).json()
    response = client.post(
        "/civic/drafts/preview",
        headers={"Authorization": "Bearer owner-a"},
        json={
            "template_id": "petition.general",
            "saved_format_id": saved["format_id"],
            "issue": "Synthetic acceptance issue: a public streetlight is not working.",
            "preview_processing_consent": True,
            "use_ai": False,
            "remote_processing_consent": False,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["template_id"] == "complaint.general"
    assert body["ai_used"] is False
    assert body["persistence"] == "not_persisted"
    assert body["submission"] == "not_submitted"
    assert "Records or documents requested" not in body["draft_body"]


def test_saved_format_id_cannot_be_used_by_a_different_owner(monkeypatch):
    client, _repository = _client(monkeypatch)
    saved = _save(client).json()
    response = client.post(
        "/civic/drafts/preview",
        headers={"Authorization": "Bearer owner-b"},
        json={
            "template_id": "complaint.general",
            "saved_format_id": saved["format_id"],
            "issue": "Synthetic issue.",
            "preview_processing_consent": True,
        },
    )
    assert response.status_code == 404


def test_saved_format_provider_is_registered_as_a_persistence_domain():
    assert "citizen_document_format" in PERSISTED_DOMAINS


def test_format_migration_defines_owner_scoped_forced_rls_without_source_content():
    from pathlib import Path
    migration = Path(__file__).parents[1] / "db/migrations/20261030120000_citizen_document_formats.sql"
    sql = migration.read_text(encoding="utf-8").lower()
    assert "enable row level security" in sql
    assert "force row level security" in sql
    assert sql.count("create policy citizen_document_formats_owner_") == 4
    assert "current_setting('janavani.principal_id', true)" in sql
    assert "owner_principal_id text not null" in sql
    assert "source_draft" not in sql
    assert "narrative" not in sql


def test_production_saved_formats_fail_closed_without_durable_provider(monkeypatch):
    from src.storage.repositories.citizen_document_format_provider import (
        CitizenDocumentFormatProviderConfigurationError,
        create_citizen_document_format_repository,
    )
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    monkeypatch.setenv("JANAVANI_CITIZEN_DOCUMENT_FORMAT_REPOSITORY_PROVIDER", "memory")
    monkeypatch.delenv("JANAVANI_CITIZEN_DOCUMENT_FORMAT_DSN", raising=False)
    with pytest.raises(CitizenDocumentFormatProviderConfigurationError):
        create_citizen_document_format_repository()
