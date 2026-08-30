#!/usr/bin/env python3
"""Generate a governance-oriented Markdown report from audit JSON.

The report maps evidence to KEEP / CONVERGE / ARCHIVE / DELETE / INVESTIGATE.
It never performs repository changes; stdout is the only output.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

CLASSES = ("KEEP", "CONVERGE", "ARCHIVE", "DELETE", "INVESTIGATE")


def evidence_text(finding: dict) -> str:
    signals = finding.get("signals", [])
    return "; ".join(str(s) for s in signals) if signals else "no evidence signal supplied"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Janavani governance audit Markdown from JSON")
    parser.add_argument("input", help="JSON produced by janavani_repo_audit.py --json")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date, YYYY-MM-DD")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    grouped: dict[str, list[dict]] = {name: [] for name in CLASSES}
    categories = Counter(str(f.get("category", "UNKNOWN")) for f in findings)
    confidence = Counter(str(f.get("confidence", "UNKNOWN")) for f in findings)

    for f in findings:
        cls = str(f.get("suggested_classification", "INVESTIGATE"))
        grouped.setdefault(cls, []).append(f)

    print(f"# Janavani Repository Governance Audit — {args.date}")
    print()
    print("> Read-only evidence report. Classifications are review guidance; no destructive action is performed by the auditor.")
    print()
    print("## Executive summary")
    print()
    print(f"- Tool version: **{data.get('version', 'unknown')}**")
    print(f"- Total findings: **{len(findings)}**")
    print(f"- Confidence: HIGH **{confidence['HIGH']}**, MEDIUM **{confidence['MEDIUM']}**, LOW **{confidence['LOW']}**")
    print(f"- Legacy-generation signals enabled: **{data.get('legacy_generation_signals', False)}**")
    print()

    print("## Governance classification")
    print()
    print("| Class | Findings | Governance meaning | Default disposition |")
    print("|---|---:|---|---|")
    meanings = {
        "KEEP": ("Canonical, active, generated, or required", "Maintain and test"),
        "CONVERGE": ("Useful but duplicated or misplaced", "Move/adapt toward canonical owner"),
        "ARCHIVE": ("Historical or uncertain and not required for current runtime", "Isolate with provenance; verify first"),
        "DELETE": ("Confirmed obsolete and unused", "Remove only after dependency/runtime/history evidence"),
        "INVESTIGATE": ("Evidence is insufficient or ambiguity remains", "Do not modify yet"),
    }
    for cls in CLASSES:
        meaning, disposition = meanings[cls]
        print(f"| {cls} | {len(grouped[cls])} | {meaning} | {disposition} |")
    print()

    print("## Findings by category")
    print()
    for category, count in sorted(categories.items()):
        print(f"- `{category}`: {count}")
    if not categories:
        print("No findings were reported.")
    print()

    for cls in CLASSES:
        print(f"## {cls}")
        print()
        items = grouped[cls]
        if not items:
            print("None reported.")
            print()
            continue
        for idx, f in enumerate(items, 1):
            print(f"### {idx}. `{f.get('path', 'unknown')}`")
            print(f"- Category: `{f.get('category', 'UNKNOWN')}`")
            print(f"- Confidence: **{f.get('confidence', 'UNKNOWN')}**")
            print(f"- Evidence: {evidence_text(f)}")
            print(f"- Destructive action allowed by tool: **{f.get('destructive_action_allowed', False)}**")
            if cls == "DELETE":
                print("- Required before deletion: dependency, runtime, test, configuration, deployment, and history evidence.")
            elif cls == "ARCHIVE":
                print("- Required before archive: verify it is not a current runtime dependency and preserve provenance.")
            elif cls == "CONVERGE":
                print("- Required before convergence: identify the canonical owner and migrate consumers/tests safely.")
            elif cls == "KEEP":
                print("- Action: retain; verify tests and ownership remain current.")
            else:
                print("- Action: investigate; do not remove or rewrite from this signal alone.")
            print()

    print("## Legacy-generation review protocol")
    print()
    print("Legacy-generation signals are intentionally conservative. A candidate requires independent evidence such as overlapping modules, parallel definitions, migration/deprecation language, or references to a legacy module.")
    print()
    print("```text")
    print("signal → collect evidence → identify canonical owner → inspect consumers")
    print("       → inspect runtime/tests/configuration/history → classify")
    print("       → converge/archive/delete only when evidence supports it")
    print("```")
    print()

    print("## Recommended execution order")
    print()
    print("1. KEEP: protect canonical and required infrastructure from cleanup drift.")
    print("2. CONVERGE: reduce duplicate generations toward one shared capability owner.")
    print("3. INVESTIGATE: resolve ambiguous legacy/orphan/migration/security signals.")
    print("4. ARCHIVE: isolate confirmed historical material with provenance when deletion is not yet justified.")
    print("5. DELETE: use only for confirmed obsolete and unused material after full evidence review.")
    print()
    print("## Shared-infrastructure governance rule")
    print()
    print("> Janavani's first engineering priority is repository cleanup and convergence, in parallel with building shared infrastructure. New product features must not create another channel-specific or generation-specific implementation when a reusable capability belongs in the shared platform.")
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
