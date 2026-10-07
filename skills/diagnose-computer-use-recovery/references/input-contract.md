# Local triage input
Python3.9+ standard library only. From the skill directory:
```text
python scripts/triage.py /absolute/private/input.local.json --output /absolute/private/new-report.json
```
Use an existing allowed Python runtime. The output parent must exist; an existing output is rejected. The helper accepts UTF-8/BOM and Unicode/space paths. It never reads Codex configuration or process lists, launches native tools, sends data, or repairs settings.

Minimal input:
```json
{
  "error": "helper_unknown_error: setup refresh had errors",
  "same_attempt": true,
  "setup_excerpt": "runtime read/execute validation failed on node_repl.exe (os error 32)",
  "desired_mode": "elevated",
  "observed_mode": "elevated",
  "cli_probe": "PASS",
  "checks": {"kernel": "FAIL", "import": "NOT_RUN"},
  "required_capabilities": ["kernel","import","windows","state","capture","geometry","input"],
  "post_relaunch": false,
  "restarts_attempted": 1,
  "restoration_state": "VERIFIED"
}
```
Keep this raw input local; real excerpts may contain private paths. same_attempt is true only after matching error time/session and runtime path/version. False/missing means excerpts are not used as current root-cause evidence. Required capabilities must reflect the user's task, not be weakened to hide failure.
Checks are PASS/FAIL/NOT_RUN from the SAME observed session. Modes are elevated/unelevated or omitted if unknown. post_relaunch is a boolean indicating independent verification after the applicable relaunch. Restart count covers this same failure signature, including prior turns, not just the current turn.
The report is an allowlisted classification/check summary; raw text is omitted. User/agent supplied check assertions are not independently proven by this parser. Review even a sanitized summary before sharing. No status claims a permanent fix.

The helper can distinguish runtime os32, runtime os5, logon1385, helper timeout, capture timeout, geometry and unavailable native APIs. A sharing classification proves only the logged failure mechanism, not the lock-holder process or the Windows/Codex code defect. Unrecognized errors remain unknown.

restoration_state is UNKNOWN (default), NOT_NEEDED, PENDING, VERIFIED, or BLOCKED. Report preserves intended/effective modes, temporary_mode, post_relaunch and requested_checks separately from all observed checks. PARTIAL requires at least one requested capability to pass; requested failures with no requested successes are BLOCKED. Successful diagnostic checks outside required_capabilities do not upgrade this status. stop_restarting=true removes the cold-restart recommendation after the consumed experiment.
