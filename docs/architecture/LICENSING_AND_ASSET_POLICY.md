# JanaVani Component Licensing and Asset Policy

**Status:** Proposed governance policy for maintainer/legal review  
**Reviewed:** 29 October 2026

## 1. Executive decision

JanaVani should use a **component-level licensing portfolio**, not attach every listed licence to the whole repository or randomly change licence by folder. Each independently reusable component must have one clearly stated outbound licence, ownership/provenance metadata, and compatibility review for its dependency graph.

The canonical Janavani repository currently ships a top-level GNU GPL version 3 licence. Preserve that licence for the existing platform and bot code unless the actual copyright holders approve a documented change. Do not relicense historical code simply to make the portfolio look diverse.

The showcase repository `netzen-abm/janavani-website` has a root MIT licence. This candidate imports only its small 327-byte JanaVani brand mark as a packaged asset, adds source attribution, and preserves a separate reservation of brand/trademark rights. The mark is served by both web surfaces from the application bundle; product runtime does not depend on the showcase repository being available.

This is an engineering policy proposal, not a legal opinion. Before a public release or any dual-licensing offer, verify contributor ownership/assignment, all dependency licences, trademark rights and jurisdiction-specific obligations with qualified counsel.

## 2. Current scope vs proposed future choices

| Component | Current or intended scope | Suggested licence | Why / guardrail |
|---|---|---|---|
| Existing Janavani platform, canonical API, Telegram bot and shared capabilities | Existing repository code | **GPL-3.0-only** (retain root licence) | The current root `LICENSE` is the GNU GPL version 3 text. Do not silently relicense existing files. Distributed derivatives must satisfy GPLv3 obligations. |
| Brand mark copied from the showcase repository | `src/ui/assets/brand/janavani-mark.svg` | MIT copyright licence for the asset, based on the source repository's MIT terms, with **brand/trademark rights reserved** | Source is identified in the adjacent asset attribution file. MIT permission for copyright does not grant a right to use JanaVani's name/logo as endorsement or to imply affiliation. Confirm asset rights before external reuse. |
| Standalone public SDK, command-line tools, or generated API client | Only if later extracted as an independently versioned package | Apache-2.0 **or** MIT/BSD-2-Clause per package | Apache-2.0 provides an express patent grant and patent-termination terms; MIT/BSD are simpler permissive terms. Choose one per package; do not dual-license accidentally. |
| Small standalone examples or reference adapters | Only if maintained as independent modules with minimal domain coupling | MIT or BSD-2-Clause; BSD-3-Clause when its no-endorsement clause is desired | Keep any source notices and third-party notices. Do not use BSD-3 endorsement language as a substitute for brand policy. |
| Independently reusable plugin with a file-level reciprocity goal | Only if genuinely separable from GPL core and independently maintained | MPL-2.0 | Modified MPL-covered files stay under MPL's file-level copyleft; compatibility and any combined distribution still require review. |
| Replaceable shared library where users must be able to relink a modified library | Only for a stable, independently consumable library | LGPL-3.0-or-later | Useful for a genuine shared-library boundary, not a reason to split cohesive Python modules merely to use another licence. Confirm linking/replacement mechanics in all distribution formats. |
| A separately deployable hosted service intended to require publication of service-side modifications | Only as a separately governed service/package after dependency and ownership review | AGPL-3.0-only or AGPL-3.0-or-later, selected explicitly | AGPL has network-interaction source obligations for modified versions. Do not apply AGPL to the existing repository by label alone or assume a combined GPL/AGPL distribution is automatically compliant. |
| Eclipse-ecosystem component or standalone module that deliberately adopts Eclipse governance | Only where the project's ecosystem justifies it | EPL-2.0, **only after compatibility review** | Confirm the exact EPL-2.0 Secondary License notice and its compatibility with dependencies and any combined GPL distribution. It is not the default for Janavani Python code. |
| Written documentation, guides, and non-code educational content | Only when the relevant authors control rights and the scope is explicitly marked | Prefer CC BY 4.0 for independently licensed prose; otherwise retain the repository's current applicable notice | Code licences are not automatically the best fit for educational prose. Clearly exclude confidential material and third-party content. |
| Statutes, Gazette documents, judgments, third-party images, maps, fonts and datasets | Per item | The source's own reuse terms; no blanket JanaVani licence | The licence of JanaVani code or a website repository does not automatically relicense upstream government or third-party material. Record rights, attribution and retention terms in the source registry. |

## 3. Compatibility and distribution rules

1. **One default licence per independently released package.** Use one SPDX identifier in the package's `LICENSE`/metadata. Dual-licensing requires an explicit, deliberate offer with identified rights holders and terms; it is not accomplished by placing multiple license texts in a folder.
2. **File-level headers are not a shortcut.** A module inside the same application can be part of a combined/derivative work. A new per-file licence cannot make incompatible code magically separable. Use a real API/process/package boundary and dependency review before assigning a different licence.
3. **Keep provenance.** Third-party code/assets need the exact source, version/commit, original licence, any copyright/attribution text, and modifications recorded in `THIRD_PARTY_NOTICES.md` or an adjacent attribution file.
4. **Preserve source offers and notices.** GPL/AGPL, LGPL, MPL and EPL have different notice, source, modification, linking and network requirements. Validate the form of distribution (source, containers, downloadable binaries and hosted use) against the chosen terms.
5. **No licence laundering.** Do not import code/assets with unknown or incompatible terms merely because a GitHub repository is public. Public accessibility is not a licence grant.
6. **Trademarks are distinct.** No OSS licence grants the right to imply official, governmental, partner or maintainer endorsement. Reserve JanaVani brand/name/logo usage, subject to any explicit brand permission.
7. **Contributor rights must be clear.** Use a CONTRIBUTING/DCO or CLA approach chosen by maintainers. Do not promise a new outbound licence for contributions unless the contributor grant supports it.
8. **Automate evidence.** CI should inventory dependencies/licenses, flag unknown licences, ensure first-party SPDX identifiers match this policy, and verify that every imported asset has an attribution record. Exemptions require a documented owner and reason.

## 4. Concrete recommendation for JanaVani

- Keep the current product code under the existing GPLv3 terms for this engineering cycle.
- Apply the source website's MIT terms only to the identified brand mark import, with the brand reservation in the attribution notice.
- If an SDK/contract needs adoption by third-party ecosystem builders, extract it as a genuine independent package and choose Apache-2.0 **or** MIT/BSD for that package after checking code provenance.
- Consider MPL-2.0 or LGPL-3.0 only for a specific reusable component whose file/library boundary is real and tested.
- Consider AGPL-3.0 only if JanaVani intentionally wants a separately governed network service to impose AGPL obligations on modified service versions.
- Use EPL-2.0 only where the Eclipse ecosystem or its project governance creates a concrete benefit and the compatibility path is explicitly documented.
- Do not apply all the licences listed in the user request merely for completeness. Licences are alternatives with distinct obligations; use only those that fit a specific component and business/community goal.

## 5. Brand asset import record

The current asset import is intentionally small and avoids duplicating the existing 205 KB legacy favicon/logo. The source repository already contains a 327-byte `assets/brand/favicon/janavani-mark.svg`; it is now bundled once at `src/ui/assets/brand/janavani-mark.svg` and served by a shared helper to the Dynamic Web and WebApp.

For further assets, prefer optimized WebP/SVG files with verified provenance. Do not bulk-copy the large BMP/TIFF/PNG logo variants or the full homepage images without checking whether the current platform already contains duplicates and whether the visuals are appropriate for an interactive citizen workflow.

## 6. Release checklist

- [ ] Maintainer confirms all first-party code rights and any third-party contributions.
- [ ] `LICENSE` and SPDX policy are consistent; existing root GPLv3 remains unchanged.
- [ ] Asset attribution and trademark reservation are present.
- [ ] Dependency and asset licence scan is green on the exact release commit.
- [ ] Every independently licensed package has its own licence text/SPDX metadata.
- [ ] No file or module has conflicting, implied or undocumented licence terms.
- [ ] The public UI offers required notices when applicable.
- [ ] Legal review approves any use of AGPL, EPL, dual licensing or a relicensing change.
