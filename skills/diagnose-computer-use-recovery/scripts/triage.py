"""Classify a supplied local snapshot; never touches UI, settings or processes."""
import argparse
import json
import re
from pathlib import Path

CAPABILITIES = {"kernel", "import", "windows", "state", "capture", "geometry", "input"}

def triage(e):
    if not isinstance(e, dict) or not isinstance(e.get("error", ""), str):
        raise ValueError("Expected object with string error")
    if type(e.get("same_attempt", False)) is not bool:
        raise ValueError("same_attempt must be boolean")
    if not isinstance(e.get("setup_excerpt", ""), str):
        raise ValueError("setup_excerpt must be string")
    checks = e.get("checks", {})
    if not isinstance(checks, dict) or any(
        k not in CAPABILITIES or v not in ("PASS", "FAIL", "NOT_RUN")
        for k, v in checks.items()
    ):
        raise ValueError("Invalid capability checks")
    required = e.get("required_capabilities", sorted(CAPABILITIES))
    if not isinstance(required, list) or not required or any(
        not isinstance(k, str) or k not in CAPABILITIES for k in required
    ):
        raise ValueError("Invalid required capabilities")
    restarts = e.get("restarts_attempted", 0)
    if type(restarts) is not int or restarts < 0:
        raise ValueError("Invalid restart count")
    if type(e.get("post_relaunch", False)) is not bool:
        raise ValueError("post_relaunch must be boolean")
    for key in ("desired_mode", "observed_mode"):
        if e.get(key) not in (None, "elevated", "unelevated"):
            raise ValueError("Invalid sandbox mode")
    restoration = e.get("restoration_state", "UNKNOWN")
    if restoration not in ("UNKNOWN", "NOT_NEEDED", "PENDING", "VERIFIED", "BLOCKED"):
        raise ValueError("Invalid restoration state")

    error = e.get("error", "").casefold()
    excerpt = e.get("setup_excerpt", "").casefold() if e.get("same_attempt", False) else ""
    classification, layer = "unknown", "unknown"
    if any(s in error for s in ("setup refresh", "windows sandbox failed", "runtime read/execute validation failed")):
        layer, classification = "sandbox_setup", "sandbox_setup_unknown"
        runtime_lines = [
            line for line in (error + "\n" + excerpt).splitlines()
            if "runtime read/execute validation failed" in line
        ]
        if any(re.search(r"os error 32\b|sharing violation", line) for line in runtime_lines):
            classification = "runtime_acl_sharing_violation"
        elif any(re.search(r"os error 5\b|access.*denied", line) for line in runtime_lines):
            classification = "runtime_acl_access_denied"
        elif re.search(r"\b1385\b", error + " " + excerpt):
            classification = "sandbox_logon_policy"
    elif re.search(r"\b1385\b", error):
        layer, classification = "sandbox_setup", "sandbox_logon_policy"
    elif "native computer" in error and ("disabled" in error or "unavailable" in error):
        layer, classification = "tool_surface", "native_surface_unavailable"
    elif "framearrived" in error:
        layer, classification = "native_capture", "native_capture_timeout"
    elif "coordinate input geometry" in error:
        layer, classification = "native_input", "native_coordinate_geometry"
    elif "timed out" in error and ("sky." in error or "helper" in error):
        layer, classification = "native_helper", "native_helper_timeout"
    elif not error:
        classification = "no_error_supplied"

    requested_checks = {c: checks.get(c, "NOT_RUN") for c in sorted(set(required))}
    successes = any(v == "PASS" for v in requested_checks.values())
    failures = any(v == "FAIL" for v in requested_checks.values())
    temporary = bool(e.get("desired_mode") and e.get("observed_mode")
                     and e["desired_mode"] != e["observed_mode"])
    if layer == "sandbox_setup" or checks.get("kernel") == "FAIL" or checks.get("import") == "FAIL":
        status = "BLOCKED"
    elif failures:
        status = "PARTIAL" if successes else "BLOCKED"
    elif error:
        status = "PARTIAL" if successes else "UNRESOLVED"
    elif all(v == "PASS" for v in requested_checks.values()):
        if temporary:
            status = "TEMPORARY_WORKAROUND"
        elif e.get("observed_mode") and e.get("observed_mode") == e.get("desired_mode") and e.get("post_relaunch"):
            status = "VERIFIED_REQUESTED_CAPABILITIES"
        else:
            status = "UNVERIFIED_PERSISTENCE"
    else:
        status = "PARTIAL" if successes else "NOT_RUN"
    actions = {
        "runtime_acl_sharing_violation": ["identify_exact_lock_owner_read_only", "coordinate_one_authorized_cold_restart", "verify_native_cua_after_relaunch"],
        "runtime_acl_access_denied": ["inspect_access_and_managed_policy_read_only", "seek_authorized_admin_or_it_repair"],
        "sandbox_logon_policy": ["inspect_logon_rights_with_it", "do_not_change_policy_automatically"],
        "sandbox_setup_unknown": ["obtain_same_attempt_setup_error", "do_not_infer_root_cause_from_wrapper"],
        "native_helper_timeout": ["bounded_lightweight_retry_then_reset", "follow_installed_computer_use_guidance"],
        "native_capture_timeout": ["inspect_desktop_session_and_capture_boundary", "report_capture_not_verified"],
        "native_coordinate_geometry": ["refresh_supported_window_state", "avoid_stale_coordinates"],
        "native_surface_unavailable": ["inspect_available_native_tool_surface", "do_not_use_browser_api_as_native_ui"],
    }.get(classification, ["collect_minimum_current_boundary_evidence"])
    if restarts >= 1:
        actions = [a for a in actions if a != "coordinate_one_authorized_cold_restart"]
    return {
        "schema_version": 1, "classification": classification, "layer": layer, "status": status,
        "desired_mode": e.get("desired_mode"), "observed_mode": e.get("observed_mode"),
        "temporary_mode": temporary, "post_relaunch": e.get("post_relaunch", False),
        "restoration_state": restoration, "required_capabilities": sorted(set(required)),
        "requested_checks": requested_checks,
        "lock_holder_identified": False, "stop_restarting": restarts >= 1, "next_actions": actions,
        "checks": {k: checks.get(k, "NOT_RUN") for k in sorted(CAPABILITIES)},
        "raw_input_included": False, "automatic_mutation_performed": False,
        "limitations": ["Evidence supplied by caller; no live root-cause proof",
                       "CLI probe does not establish Computer Use recovery",
                       "Verification is limited to declared capabilities and session"],
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    try:
        result = triage(json.loads(a.input.read_text(encoding="utf-8-sig")))
        with a.output.open("x", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except (OSError, ValueError):
        # Do not echo private paths, raw JSON, setup logs or exception contents.
        p.exit(2, "TRIAGE_FAILED: invalid input, unreadable input, or unavailable output; preserve local evidence\n")
    print("TRIAGE_WRITTEN")

if __name__ == "__main__":
    main()
