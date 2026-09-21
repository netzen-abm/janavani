#!/usr/bin/env python3
"""Safely retire legacy Janavani branches.

Default mode is dry-run. A branch is eligible for automatic retirement only when:
- it is not one of the nine sanctioned long-lived roles;
- it has zero commits ahead of main;
- it has no open pull request;
- its remote ref still exists.

Divergent branches are deliberately left for selective extraction and review.
Run with --execute only after reviewing the dry-run output.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

REPO = "netzen-abm/janavani"
BASE = "main"
SANCTIONED = {
    "main",
    "integration/canonical-platform",
    "feat/canonical-case-kernel",
    "feat/canonical-capability-execution-envelope",
    "feat/canonical-civic-action-vertical-slice",
    "feat/canonical-sos-contract",
    "feat/capability-scoped-consent-agent-enforcement",
    "audit/postgres-provider-production-gates",
    "chore/ecosystem-shared-capability-infrastructure",
}


def gh_api(path: str, *, method: str = "GET") -> Any:
    command = ["gh", "api", "--method", method, path]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def branches() -> list[str]:
    rows = gh_api(f"repos/{REPO}/branches?per_page=100")
    names = [row["name"] for row in rows]
    page = 2
    while len(rows) == 100:
        rows = gh_api(f"repos/{REPO}/branches?per_page=100&page={page}")
        names.extend(row["name"] for row in rows)
        page += 1
    return names


def compare(branch: str) -> dict[str, Any]:
    return gh_api(f"repos/{REPO}/compare/{BASE}...{branch}")


def open_prs(branch: str) -> list[dict[str, Any]]:
    return gh_api(
        f"repos/{REPO}/pulls?state=open&head=netzen-abm:{branch}&per_page=100"
    )


def eligible(branch: str) -> tuple[bool, str]:
    if branch in SANCTIONED:
        return False, "sanctioned role"
    comparison = compare(branch)
    ahead = comparison.get("ahead_by", 0)
    if ahead != 0:
        return False, f"{ahead} commit(s) ahead of main; selective extraction required"
    prs = open_prs(branch)
    if prs:
        return False, f"{len(prs)} open pull request(s)"
    return True, "fully contained in main and no open PR"


def delete_branch(branch: str) -> None:
    gh_api(
        f"repos/{REPO}/git/refs/heads/{branch}",
        method="DELETE",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually delete eligible remote refs; default is dry-run",
    )
    args = parser.parse_args()

    names = branches()
    print(f"Observed physical branches: {len(names)}")
    print(f"Sanctioned long-lived roles: {len(SANCTIONED)}")

    eligible_branches: list[str] = []
    for branch in names:
        ok, reason = eligible(branch)
        status = "DELETE" if ok else "HOLD"
        print(f"{status:6} {branch}: {reason}")
        if ok:
            eligible_branches.append(branch)

    if not args.execute:
        print("\nDry-run only. Re-run with --execute after reviewing the DELETE set.")
        return 0

    for branch in eligible_branches:
        print(f"Deleting {branch}...")
        delete_branch(branch)

    remaining = branches()
    print(f"Remaining physical branches: {len(remaining)}")
    if len(remaining) != len(SANCTIONED):
        print(
            "Retirement incomplete: divergent branches still require selective "
            "extraction/review before deletion.",
            file=sys.stderr,
        )
        return 2
    print("Physical branch budget is now exactly nine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
