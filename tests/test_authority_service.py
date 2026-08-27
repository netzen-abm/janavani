from pathlib import Path

import pandas as pd

from src.services.authority_service import find_authorities


def test_find_authorities_returns_domain_objects(tmp_path: Path) -> None:
    data_file = tmp_path / "offices.csv"
    pd.DataFrame(
        [
            {
                "type": "Revenue",
                "city": "Bengaluru",
                "name": "Revenue Office",
                "address": "District Complex",
                "phone": "080-1234",
                "website": "https://example.gov.in",
            },
            {
                "type": "Health",
                "city": "Bengaluru",
                "name": "Health Office",
            },
        ]
    ).to_csv(data_file, index=False)

    results = find_authorities("revenue", "bengaluru", data_file=data_file)

    assert len(results) == 1
    assert results[0].name == "Revenue Office"
    assert results[0].jurisdiction["city"] == "Bengaluru"
    assert results[0].verification_status.value == "unverified"
    assert results[0].source_refs[0].source_id == "office-directory-csv"


def test_find_authorities_rejects_blank_filters(tmp_path: Path) -> None:
    data_file = tmp_path / "offices.csv"
    pd.DataFrame([{"type": "Revenue", "city": "Bengaluru"}]).to_csv(data_file, index=False)

    for department, location in [("", "Bengaluru"), ("Revenue", "")]:
        try:
            find_authorities(department, location, data_file=data_file)
        except ValueError:
            pass
        else:
            raise AssertionError("blank lookup filters should be rejected")
