# Xoom Pi canonical project archive

Prepared Oct 18, 2026; 107 version-indexed ZIP/image artifacts, plus two DC runtime archives and Surface source snapshot. The Pi owns private, hash-verified binaries and source; a sanitized mirror goes to GitHub only after audit. Original sources, files and dated reports are preserved unmoved.

Read recovery/README.md and recovery/CHANGELOG.md for image history, or packages/<ID>/README.md and CHANGELOG.md for each package. Private artifact inventory: private/project-archive/ARTIFACT-INDEX-2026-10-18.json.

Important: historical document status is temporal. Currently v6D is deliberately live, v0.5.1 callback permission issue remains unresolved; Desktop Commander 0.16.0 is proven RAM/cloud prototype but not pinned into Toolkit. Windows WSL is the primary native build workspace, Surface USB ADB is the hardware verifier, Pi owns final image and backups.

GitHub publication pending: review for credentials, private code/rights, and reconcile current Pi checkout with newer origin/main before pushing. Do not bulk-add the dirty worktree.

## Revision navigation

Every archived image or package ZIP has an individual versions/<series>/<artifact>/README.md with exact digest, original source and a status/evidence warning. This is the first pass: source-to-version mapping and full QA lineage should be enriched from dated builders/tests before claiming a complete project release history.

## Latest hardware audit

- Oct 18 v6D cold reboot: recovery USB ADB survived, but normal Wi-Fi autoload failed INNER_PIN_MISMATCH. See recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md. A prior manually/live-established Wi-Fi state must not be treated as a cold-boot pass.

## Cumulative machine archive and reconciliation

Read the [October 18 cross-machine source map](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md) for the newly unified private Pi backup, source provenance per package and recovery, exact current partition readback, and GitHub publication safeguards.

## Legacy source reconciliation update — 2026-10-18

51 conservatively screened historical Pi source files were restored to the public repository without modifying the old Pi checkout. The other 78 unique untracked files remain checksum-preserved in the private archive for closer review; 131 old untracked archive documents already matched GitHub exactly. See [the legacy source status](LEGACY-PI-SOURCE-RECONCILIATION-2026-10-18.md) for the distinction.
