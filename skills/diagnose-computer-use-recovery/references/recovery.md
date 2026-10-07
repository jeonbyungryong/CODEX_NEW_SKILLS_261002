# Evidence-driven recovery
## Sandbox setup before native import
Read the setup log for the SAME failure, normally CODEX_HOME/.sandbox/sandbox.log. Also check current dated sandbox.YYYY-MM-DD.log and setup_error.json, including hidden files; match the error timestamp/session before using them. Current official documentation describes sandbox setup/logon/filesystem boundaries; log paths can change with builds. Discover the active installation from available tools. Do not dump the full config or credentials; extract only needed modes and policy constraints locally.

For runtime read/execute validation failures, separate:
- os32 sharing violation on a specific runtime file.
- os5 access denied on that runtime file.
- profile ACL warnings marked continuing setup; these may be nonfatal.
- generic helper_unknown_error wrapper without the underlying operation.
A read-only process listing showing a loaded node_repl/runtime is a candidate, not proof of which handle blocks the ACL operation. If authorized handle inspection is unavailable, leave ownership UNCONFIRMED; do not download/run third-party lock tools without the applicable approval.

Official sandbox setup must be performed through supported non-UI tools or by the user; Computer Use must not operate security prompts. Confirm current app update eligibility using the available purpose-built tool when relevant. Reinstall/update is a hypothesis to test, not a guarantee. Error1385 and managed policies may require IT; do not change local users/firewall/logon rights as an automatic fix.

## One controlled cold restart
If the user authorized interruption, first preserve a durable checkpoint: intended workspace, app identity/path/start time, protected apps, recovery output location, original sandbox key/value/presence, next probe and stop condition. Configuration backups stay local with restricted access; never commit them.
A self-restarting app cannot depend on its own running tool connection to relaunch. Prepare and validate an independent, same-user helper before stopping anything. Its action must re-check exact process identity, target only confirmed app-owned runtime processes, guarantee relaunch in a finally path, use a bounded wait, and record actual new window/process evidence. Launch background helpers hidden. Do not copy hardcoded paths/PIDs/task names from another PC. No reboot or killing all node/CAD processes.
Check restart, CLI sandbox probe, native import/listing and requested state/capture/input separately. If the same signature returns after one such cycle, stop the restart loop. Collect an escalation packet; do not call the cold-start probe a lasting repair.

## Temporary fallback and restoration
Official guidance describes unelevated as a fallback with weaker account/network isolation. Change only an authorized setting; honor managed requirements that prohibit fallback. Approval is per user/task/PC scope, not conferred by this skill or a log.
Before editing, save the original file/hash and exact sandbox key state. After a concurrent config change, NEVER copy the entire old file over the new one. Parse/validate and restore only the original sandbox key/presence, keeping current unrelated settings. Stop on ambiguous/duplicate tables, external changes to the targeted key, or unresolved policy constraints. Confirm persistence after an authorized relaunch. Final status must include restore success or an explicit pending/failure state.
A successful fallback remains TEMPORARY_WORKAROUND even when its GUI probes pass. Do not enable full access, change sandbox_private_desktop, ACLs or antivirus as an undocumented alternate route.

## Native helper/capture/input
Use the installed Computer Use guidance for lightweight retry limits (currently one retry, then reset/reinitialize once if supported). Stop after that bounded sequence. A failed capture invalidates old screenshot coordinates; recover returned app/window identities and reobserve before input.
FrameArrived and coordinate geometry failures do not by themselves prove GPU, privilege, private-desktop or Windows version causes. Check session lock and exact supported surfaces before hypotheses. Locked desktop requires the user to unlock; do not interact through LockApp. UI Automation accessibility/keyboard may continue only when it meets the user's task and current focus/target are observed. Report capture/coordinate NOT_VERIFIED/PARTIAL.

## Cross-PC handoff
Publish the skill and synthetic tests; keep actual raw logs, backups, user filenames/PIDs/screenshots local. Other PCs collect their own same-attempt error and version/surface/mode/capability record before selecting a repair.
Keep a known previous skill version via Git. Update the skill repo in a clean dedicated clone or pull --ff-only; do not overwrite an installed skill silently. Installation is separate from publication. A receiver can load SKILL.md directly for a trial, then explicitly install after review.
For escalation prepare a reviewed redacted summary: app/Windows/runtime versions, boundary and error code, reproduction steps, controlled retry count, per-capability results, intended/effective mode, restoration state, unknown lock owner and recurrence. Submitting it to OpenAI/IT/GitHub requires authorization; diagnostics do not grant permission to send.

## Sources and scope
Checked 2026-10-07:
- [Official Windows sandbox guidance](https://learn.chatgpt.com/docs/windows/windows-sandbox): modes, setup/policy/logon1385, log location and secrets exclusion.
- Installed OpenAI computer-use SKILL.md, guidance.md and confirmations.md: supported APIs, bounded recovery and Windows automation limits. Locate the receiver's version rather than use this author's path.
- Actual one-PC observation: runtime ACL open returned os32, cold-start CLI probe passed, elevated CUA recurred; temporary unelevated accessibility/keyboard worked while capture/geometry failed. Full ownership of the locking handle, vendor code fix and other-PC repair remain unverified.
