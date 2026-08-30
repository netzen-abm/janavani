"""Migration evidence adapter using local content-addressed files."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import uuid

from capabilities.evidence import EvidenceCapability, EvidenceItem, EvidenceResult


class LocalEvidenceCapability(EvidenceCapability):
    def __init__(self, root: str = "database/evidence"):
        self.root = Path(root)

    def add(self, *, case_id, evidence_type, source_channel, filename=None,
            content_type=None, storage_reference=None, sha256=None, metadata=None):
        evidence_id = f"EVD-{uuid.uuid4().hex[:10].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        digest = sha256
        if storage_reference and Path(storage_reference).is_file() and not digest:
            digest = hashlib.sha256(Path(storage_reference).read_bytes()).hexdigest()

        item = EvidenceItem(
            evidence_id=evidence_id,
            case_id=case_id,
            evidence_type=evidence_type,
            source_channel=source_channel,
            created_at=created_at,
            filename=filename,
            content_type=content_type,
            storage_reference=storage_reference,
            sha256=digest,
            metadata=metadata or {},
        )
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            with (self.root / f"{evidence_id}.json").open("w", encoding="utf-8") as handle:
                import json
                json.dump(item.__dict__, handle, ensure_ascii=False, indent=2)
        except OSError:
            return EvidenceResult(ok=False, error_code="evidence_persistence_failed", message="Evidence could not be saved.")
        return EvidenceResult(ok=True, evidence=item)

    def list(self, *, case_id):
        import json
        results = []
        if not self.root.exists():
            return results
        for path in self.root.glob("EVD-*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("case_id") == case_id:
                    results.append(EvidenceItem(**data))
            except (OSError, ValueError, TypeError):
                continue
        return results
