# 24-skill bundle verification — 2026-10-16

## Scope

The approved catalog is five unchanged user skills plus all 12 text-to-cad distribution skills, all six ponytail skills, and REA's one end-user investigation skill. Every selected upstream directory is copied in full. Three REA-maintainer skills are intentionally excluded and named in the provenance lock. The source repositories, exact commits, original paths, file SHA-256 and license hashes are retained in `third_party/upstream-lock.json`.

No CAD/REA runtime, MCP registration, browser/printing/manufacturing action, npm/pip package, or installed user skill/configuration was changed on the author's PC. The tests install only into freshly created disposable directories. CI may install its own YAML parser on ephemeral GitHub runners; that is not an installation on the author's PC.

## Local observations

- Before implementation, all 10 initial package/install tests failed because the bundle implementation did not exist. The additional ownership-boundary test subsequently reproduced acceptance of an unowned lock entry before the guard was added.
- Current bundle suite: **15 tests PASS**. It exercises a real 24-package install into a temporary destination, complete support-file copying, identical reinstallation skip, changed-name and renamed-folder identity conflicts, all-package preflight before writes, unsafe paths/source overlap, missing references, incorrect frontmatter identity, lock hashes/ownership, CLI failure codes, and unchanged-upstream no-write behavior.
- Updater cases use an external-network response double only at GitHub API/download boundaries. The actual staging, Git blob verification, file copying and validation run against real temporary files. A valid update preserves the local skill; changed license and missing references stop before repository writes.
- Existing computer-use recovery suite: **18 tests PASS**, with no changes to that suite or its skill. A first sandboxed run encountered WinError 5 in the sandbox temporary directory (all new test setups and one existing CLI case); the successful runs used an approved process with normal disposable-directory access. No ACL/sandbox/app repair was attempted.
- Actual initial import: **113 external/source-notice files**. Their contents were verified against pinned upstream Git blobs; `validate` accepted 24 unique packages and their entrypoint references. The later live `sync` returned `changed: false` for the same three commits.
- PyYAML is absent from the author's bundled Python, so the installed system `quick_validate.py` could not be used there without adding a dependency. No dependency was installed to hide that limit. The workflow separately parses all 24 frontmatters and upstream UI YAML on disposable Windows/Linux runners. This is YAML/identity validation, not a claim that every upstream optional field conforms to every version of a strict authoring helper.

## Continuous verification

The workflow runs the 15 package tests, the existing 18 tests, package/lock validation and YAML parsing on both Ubuntu and Windows. The hourly/manual updater validates again before publishing an automation branch. GitHub run results, not the presence of this workflow file, establish actual hosted execution.

The repository's existing Actions policy does not allow workflow-created/approved PRs. It is not silently changed. When that policy blocks PR creation, the update branch and compare link remain available for manual review; no upstream update is automatically merged into main or installed on PCs.

## Limits

These are packaging, preservation and installation-contract checks, not independent model-behavior evals for all third-party skills. Full CAD creation/rendering, REA providers/MCP, ponytail hooks, manufacturing accounts and real remote-PC discovery/implicit selection were not exercised. Imported optional metadata and plugin-oriented names remain upstream-original. The install planner sees its explicit destination; active plugin/other-project conflicts must also be checked by the installing agent.
