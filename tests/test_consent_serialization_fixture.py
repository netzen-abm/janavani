import json
from pathlib import Path

from src.core.consent import Consent, ConsentGrantType, ConsentStatus

FIXTURE = Path(__file__).parent / "fixtures" / "consent_serialization.json"


def test_python_consent_round_trips_canonical_fixture() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    consent = Consent(
        consent_id=payload["consent_id"],
        subject_id=payload["subject_id"],
        purpose=payload["purpose"],
        scope=tuple(payload["scope"]),
        grant_type=ConsentGrantType(payload["grant_type"]),
        status=ConsentStatus(payload["status"]),
        created_at=payload["created_at"],
        expires_at=payload["expires_at"],
        revoked_at=payload["revoked_at"],
        proof_ref=payload["proof_ref"],
    )
    encoded = {
        "consent_id": consent.consent_id,
        "subject_id": consent.subject_id,
        "purpose": consent.purpose,
        "scope": list(consent.scope),
        "grant_type": consent.grant_type.value,
        "status": consent.status.value,
        "created_at": consent.created_at,
        "expires_at": consent.expires_at,
        "revoked_at": consent.revoked_at,
        "proof_ref": consent.proof_ref,
    }
    assert encoded == payload
