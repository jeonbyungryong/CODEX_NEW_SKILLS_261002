---
name: diagnose-computer-use-recovery
description: Use when Windows Codex Computer Use repeatedly fails with setup refresh errors, node_repl startup failures, runtime file locks, helper timeouts, FrameArrived capture errors, or missing coordinate geometry.
---
# Diagnose Computer Use recovery
Identify the failing boundary and restore the requested capability without losing user work. This skill guides investigation; it is not a patch for Codex binaries.

## Start with evidence
Read the installed Computer Use SKILL.md and its required runtime/confirmation references before native UI work. Use its official APIs. Browser-only CUA and Windows-native @oai/sky are separate surfaces; discover the current tools rather than assume one replaces the other.
Record the current attempt: Windows/app/runtime version, native tool, failure stage, intended/effective sandbox mode, and requested capabilities. Keep exact errors/current setup logs locally. Never publish config.toml, auth data, .sandbox-secrets, raw process command lines, window titles, user paths or screenshots by default.

For structured local snapshots use [scripts/triage.py](scripts/triage.py); see [the input contract](references/input-contract.md). It only classifies supplied evidence and creates a new report. It neither collects logs nor changes the PC. If Python is unavailable, use the decision table manually; do not install dependencies just to run this helper.

## Route the failure
| Observation | First investigation |
|---|---|
| Kernel exits before sky import, setup refresh had errors | Current underlying sandbox setup error, not a UI selector |
| Same-attempt runtime read/execute validation + os error32 | Sharing violation at ACL validation; identify lock owner separately |
| Runtime os error5 / 1385 | Filesystem access / sandbox logon policy; read-only checks, appropriate IT/admin route |
| Import/window listing works; FrameArrived fails | Native capture/session boundary; keyboard success does not prove screenshots |
| Coordinate geometry unavailable | Fresh official state/window binding; do not reuse coordinates |
| Lightweight helper timeout | Installed guidance's bounded retry/reset; no unbounded helper launches |
| Browser works; native disabled | Tool-surface availability; do not invent native support |

A generic wrapper or another PC's diagnosis is insufficient. Historical or nonfatal profile errors must not explain a new runtime failure. See [investigation and recovery](references/recovery.md) only for the relevant branch.

## Recover proportionally
Read-only inspection and harmless fresh probes can proceed. Prefer the supported updater/setup path after confirming installed version and current official guidance. A cold restart may release a lock but is only one authorized experiment; after recurrence stop repeating it and retain evidence.
Before interruptions, prepare a checkpoint and verify the exact app/runtime identities. Protect unrelated unsaved applications. Never kill processes by name. Do not automate Codex UI, terminals/Run or security/authentication dialogs through Computer Use.
A temporary unelevated fallback needs applicable authorization, documented weaker isolation, backup and verified restoration of the original sandbox key/presence. Preserve concurrent unrelated settings. Existing explicit approval remains valid for its scope; avoid asking again. Do not disable the sandbox, alter ACL/firewall/logon/antivirus/private-desktop policy, reinstall or reboot merely to suppress a symptom.

## Verify and stop
Use fresh official bindings and a harmless test window. Record kernel/import/window listing/state and the user's required capture/geometry/input capabilities individually. CLI success, restarted app, keyboard-only success and temporary-mode success are different results.
Restore approved temporary settings, verify relaunch and requested capabilities in the intended mode, and check protected work. Recurrence or unavailable access means BLOCKED/UNRESOLVED; capture failure with requested keyboard success means PARTIAL; failure of the sole requested capture capability is BLOCKED. Report temporary mode and restoration state separately. VERIFIED applies only to evidenced requested capabilities, never permanent/all-PC repair.
For another PC, collect its own evidence and follow [cross-PC handoff](references/recovery.md#cross-pc-handoff). Report cause evidence, unknowns, actions, rollback state and the next bounded step.
