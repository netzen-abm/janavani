from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURFACE_ROOTS = (
    ROOT / "src" / "web",
    ROOT / "src" / "commands",
    ROOT / "src" / "adapters",
)


def test_surface_modules_do_not_define_parallel_civic_case_implementations() -> None:
    forbidden = ("class CivicCaseCapability", "class EvidenceCapability", "class ConsentCapability")
    for root in SURFACE_ROOTS:
        for path in root.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert not any(token in source for token in forbidden), path


def test_shared_ecosystem_contract_exists() -> None:
    contract = ROOT / "docs" / "architecture" / "SHARED_ECOSYSTEM_INFRASTRUCTURE_CONTRACT.md"
    assert contract.exists()
