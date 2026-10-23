#!/usr/bin/env python3
"""Safely archive and retire legacy Janavani branches.

Default mode is dry-run. A branch is eligible for generic retirement only when:
- it is neither one of the eight sanctioned active roles nor the controlled
  retirement-only transition branch;
- it has zero commits not contained in main and its tree matches main;
- it has no open pull request;
- the GitHub branch head matches the fetched Git ref.

The exact branch head is tagged before deletion and verified again before the
branch ref is deleted. Divergent branches are held for selective extraction.
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
    "feat/canonical-civic-action-vertical-slice",
    "feat/canonical-sos-contract",
    "feat/capability-scoped-consent-agent-enforcement",
    "audit/postgres-provider-production-gates",
    "chore/ecosystem-shared-capability-infrastructure",
}
RETIREMENT_ONLY = {"feat/canonical-capability-execution-envelope"}


def gh_api(path: str, *, method: str = "GET", fields: dict[str, str] | None = None) -> Any:
    command = ["gh", "api", "--method", method, path]
    for key, value in (fields or {}).items():
        command.extend(["-f", f"{key}={value}"])
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


def open_prs(branch: str) -> list[dict[str, Any]]:
    return gh_api(
        f"repos/{REPO}/pulls?state=open&head=netzen-abm:{branch}&per_page=100"
    )


def fetch_and_verify_git_ref(branch: str, expected_sha: str) -> tuple[bool, str]:
    remote_ref = "refs/remotes/origin/retirement-candidate"
    subprocess.run(
        [
            "git", "fetch", "--no-tags", "origin",
            f"+refs/heads/{branch}:{remote_ref}",
            f"+refs/heads/{BASE}:refs/remotes/origin/{BASE}",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    fetched_sha = subprocess.run(
        ["git", "rev-parse", remote_ref], check=True, text=True, capture_output=True
    ).stdout.strip()
    if fetched_sha != expected_sha:
        return False, "fetched Git ref does not match GitHub branch head"
    ahead = subprocess.run(
        ["git", "rev-list", "--count", f"refs/remotes/origin/{BASE}..{remote_ref}"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if ahead != "0":
        return False, f"{ahead} commit(s) not contained in main"
    tree_same = subprocess.run(
        ["git", "diff", "--quiet", f"refs/remotes/origin/{BASE}", remote_ref],
        check=False,
    ).returncode == 0
    if not tree_same:
        return False, "tree differs from main; selective extraction required"
    return True, "fetched head matches GitHub; zero ahead commits; tree matches main"


def current_ref_sha(branch: str) -> str:
    result = gh_api(f"repos/{REPO}/git/ref/heads/{branch}")
    return result["object"]["sha"]


def archive_tag_sha(tag: str) -> str | None:
    try:
        result = gh_api(f"repos/{REPO}/git/ref/tags/{tag}")
        return result["object"]["sha"]
    except subprocess.CalledProcessError:
        return None


def archive_before_delete(branch: str, head_sha: str, *, execute: bool) -> None:
    tag = f"archive/branches/{branch}"
    existing_sha = archive_tag_sha(tag)
    if existing_sha is not None and existing_sha != head_sha:
        raise RuntimeError(
            f"archive tag {tag} exists at {existing_sha}, not the current head {head_sha}"
        )
    if not execute:
        action = "verify existing archive" if existing_sha else "create archive tag"
        print(f"DRY RUN: would {action} {tag} @ {head_sha}, then delete {branch}")
        return
    if existing_sha is None:
        gh_api(
            f"repos/{REPO}/git/refs",
            method="POST",
            fields={"ref": f"refs/tags/{tag}", "sha": head_sha},
        )
    verified_tag_sha = archive_tag_sha(tag)
    current_sha = current_ref_sha(branch)
    if verified_tag_sha != head_sha or current_sha != head_sha:
        raise RuntimeError(
            f"ref/archive recheck failed before deletion (branch={current_sha}, archive={verified_tag_sha})"
        )
    gh_api(f"repos/{REPO}/git/refs/heads/{branch}", method="DELETE")
    if branch in branches():
        raise RuntimeError(f"branch ref {branch} still exists after delete")
    print(f"DELETED AFTER VERIFIED ARCHIVE: {branch} -> {tag} @ {head_sha}")


def eligible(branch: str) -> tuple[bool, str, str | None]:
    if branch in SANCTIONED:
        return False, "sanctioned active role", None
    if branch in RETIREMENT_ONLY:
        return False, "requires its dedicated post-merge retirement workflow", None
    prs = open_prs(branch)
    if prs:
        return False, f"{len(prs)} open pull request(s)", None
    head_sha = current_ref_sha(branch)
    ok, reason = fetch_and_verify_git_ref(branch, head_sha)
    return ok, reason, head_sha if ok else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually archive and delete eligible remote refs; default is dry-run",
    )
    args = parser.parse_args()

    names = branches()
    print(f"Observed physical branches: {len(names)}")
    print(f"Sanctioned active roles: {len(SANCTIONED)}")
    print(f"Retirement-only transition refs: {len(RETIREMENT_ONLY)}")

    eligible_branches: list[tuple[str, str]] = []
    for branch in names:
        ok, reason, head_sha = eligible(branch)
        status = "DELETE" if ok else "HOLD"
        print(f"{status:6} {branch}: {reason}")
        if ok and head_sha:
            eligible_branches.append((branch, head_sha))

    if not args.execute:
        for branch, head_sha in eligible_branches:
            archive_before_delete(branch, head_sha, execute=False)
        print("\nDry-run only. No branch or tag refs were changed.")
        return 0

    failures: list[str] = []
    for branch, head_sha in eligible_branches:
        try:
            # Recheck PR and head eligibility immediately before archival/deletion.
            ok, reason, rechecked_sha = eligible(branch)
            if not ok or rechecked_sha != head_sha:
                raise RuntimeError(reason if not ok else "branch head changed since inventory")
            archive_before_delete(branch, head_sha, execute=True)
        except Exception as exc:
            failures.append(f"{branch}: {exc}")
            print(f"HOLD: {branch}: {exc}", file=sys.stderr)

    remaining = branches()
    print(f"Remaining physical branches: {len(remaining)}")
    if failures or len(remaining) != len(SANCTIONED):
        print(
            "Retirement incomplete: inspect held refs and selectively extract useful work.",
            file=sys.stderr,
        )
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 2
    print("Physical branch budget is now exactly eight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
