#!/usr/bin/env python3
"""Generate a review-oriented Markdown report from janavani_repo_audit JSON output.

Usage:
  python scripts/janavani_repo_audit.py . --json > audit.json
  python scripts/janavani_audit_report.py audit.json > docs/audits/REPOSITORY_EVIDENCE_AUDIT_YYYY-MM-DD.md

The generator never modifies repository files; stdout is the only output.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

CLASSES = ("KEEP", "CONVERGE", "ARCHIVE", "DELETE", "INVESTIGATE", "EXPERIMENTAL")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Janavani audit Markdown from JSON")
    parser.add_argument("input", help="JSON produced by janavani_repo_audit.py --json")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date, YYYY-MM-DD")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    categories = Counter(str(f.get("category", "UNKNOWN")) for f in findings)
    confidence = Counter(str(f.get("confidence", "UNKNOWN")) for f in findings)

    grouped: dict[str, list[dict]] = {name: [] for name in CLASSES}
    for finding in findings:
        suggested = str(finding.get("suggested_classification", "INVESTIGATE"))
        grouped.setdefault(suggested, []).append(finding)

    print(f"# Janavani Repository Evidence Audit — {args.date}")
    print()
    print("> Generated from the read-only Janavani repository audit tool. Findings are review candidates, not automatic deletion instructions.")
    print()
    print("## Executive summary")
    print()
    print(f"- Total findings: **{len(findings)}**")
    print(f"- Confidence: HIGH **{confidence['HIGH']}**, MEDIUM **{confidence['MEDIUM']}**, LOW **{confidence['LOW']}**")
    print(f"- Suggested DELETE findings: **{len(grouped.get('DELETE', []))}**")
    print()
    print("## Findings by category")
    print()
    if categories:
        for category, count in sorted(categories.items()):
            print(f"- `{category}`: {count}")
    else:
        print("No findings were reported.")
    print()

    for cls in CLASSES:
        items = grouped.get(cls, [])
        print(f"## {cls}")
        print()
        if not items:
            print("None reported.")
            print()
            continue
        for finding in items:
            path = finding.get("path", "unknown")
            print(f"### `{path}`")
            print(f"- Category: `{finding.get('category', 'UNKNOWN')}`")
            print(f"- Confidence: **{finding.get('confidence', 'UNKNOWN')}**")
            signals = finding.get("signals", [])
            if signals:
                print("- Evidence signals:")
                for signal in signals:
                    print(f"  - {signal}")
            print()

    print("## Recommended review sequence")
    print()
    print("1. Validate HIGH-confidence findings first.")
    print("2. Review CONVERGE candidates against the canonical ownership map.")
    print("3. Investigate orphan, legacy, migration, and workflow-security signals.")
    print("4. Archive uncertain historical material before deletion where practical.")
    print("5. Only classify an item as DELETE after dependency, runtime, test, configuration, and history evidence supports removal.")
    print("6. Update the cleanup register after confirmed changes.")
    print()
    print("## Canonical references")
    print()
    print("- `docs/audits/CANONICAL_OWNERSHIP_MAP_2026-08-29.md`")
    print("- `docs/audits/REPO_CLEANUP_REGISTER_2026-08-29.md`")
    print("- `docs/audits/REPO_AUDIT_DECISION_FRAMEWORK.md`")
    print("- `docs/development/REPOSITORY_AUDIT.md`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
