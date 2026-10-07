"""Synthetic regression cases: no actual GUI/config/process mutations."""
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"skills"/"diagnose-computer-use-recovery"/"scripts"/"triage.py"
spec=importlib.util.spec_from_file_location("triage",SCRIPT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class TriageTests(unittest.TestCase):
 def test_wrapper_is_not_root_cause(self):
  r=module.triage({"error":"node_repl kernel exited: helper_unknown_error: setup refresh had errors"})
  self.assertEqual(r["classification"],"sandbox_setup_unknown")
 def test_same_attempt_runtime_sharing(self):
  r=module.triage({"error":"setup refresh had errors","same_attempt":True,"setup_excerpt":"runtime read/execute validation failed on cua_node/bin/node_repl.exe: open ACL target for root-only update (os error 32)"})
  self.assertEqual(r["classification"],"runtime_acl_sharing_violation")
  self.assertFalse(r["lock_holder_identified"])
 def test_old_log_does_not_explain_new_failure(self):
  r=module.triage({"error":"setup refresh had errors","same_attempt":False,"setup_excerpt":"runtime read/execute validation failed (os error 32)"})
  self.assertEqual(r["classification"],"sandbox_setup_unknown")
 def test_nonfatal_profile_error_is_not_runtime_lock(self):
  r=module.triage({"error":"setup refresh had errors","same_attempt":True,"setup_excerpt":"profile ACL (os error 32); continuing setup\nruntime read/execute validation failed (os error 5)"})
  self.assertEqual(r["classification"],"runtime_acl_access_denied")
 def test_logon_policy(self):
  self.assertEqual(module.triage({"error":"sandbox setup Windows error 1385"})["classification"],"sandbox_logon_policy")
 def test_capture_geometry_and_helper_are_distinct(self):
  for error,expected in [("FrameArrived timed out","native_capture_timeout"),("coordinate input geometry is unavailable","native_coordinate_geometry"),("sky.list_windows timed out","native_helper_timeout"),("Native computer APIs are disabled","native_surface_unavailable")]:
   self.assertEqual(module.triage({"error":error})["classification"],expected)
 def test_cli_pass_does_not_fix_kernel(self):
  r=module.triage({"error":"setup refresh had errors","cli_probe":"PASS","checks":{"kernel":"FAIL"}})
  self.assertEqual(r["status"],"BLOCKED")
 def test_workaround_not_permanent(self):
  r=module.triage({"error":"","desired_mode":"elevated","observed_mode":"unelevated","checks":{"import":"PASS","windows":"PASS"},"required_capabilities":["import","windows"],"post_relaunch":True})
  self.assertEqual(r["status"],"TEMPORARY_WORKAROUND")
 def test_partial_keyboard_is_not_full_cua(self):
  r=module.triage({"error":"FrameArrived timed out","checks":{"input":"PASS","capture":"FAIL"}})
  self.assertEqual(r["status"],"PARTIAL")
 def test_verified_requires_mode_and_relaunch(self):
  e={"error":"","desired_mode":"elevated","observed_mode":"elevated","required_capabilities":["import","windows"],"checks":{"import":"PASS","windows":"PASS"},"post_relaunch":True}
  self.assertEqual(module.triage(e)["status"],"VERIFIED_REQUESTED_CAPABILITIES")
  e["post_relaunch"]=False
  self.assertNotEqual(module.triage(e)["status"],"VERIFIED_REQUESTED_CAPABILITIES")
 def test_repeat_budget(self):
  self.assertTrue(module.triage({"error":"setup refresh had errors","restarts_attempted":1})["stop_restarting"])
 def test_private_text_not_exported(self):
  e={"error":"setup refresh had errors token=SECRET_TEST_SENTINEL C:/Users/private-name","same_attempt":True,"setup_excerpt":"runtime read/execute validation failed C:/Users/private-name/node_repl.exe (os error 32)"}
  public=json.dumps(module.triage(e))
  self.assertNotIn("SECRET_TEST_SENTINEL",public);self.assertNotIn("private-name",public)
 def test_invalid_contract_rejected(self):
  for value in [[],{"error":42},{"error":"x","same_attempt":"true"},{"error":"x","required_capabilities":[]},{"error":"x","checks":{"import":"maybe"}}]:
   with self.assertRaises(ValueError):module.triage(value)
 def test_cli_unicode_and_no_overwrite(self):
  with tempfile.TemporaryDirectory(prefix="cua test ") as d:
   source=Path(d)/"한글 입력.json";target=Path(d)/"결과.json"
   source.write_text(json.dumps({"error":"FrameArrived timed out"}),encoding="utf-8-sig")
   first=subprocess.run([sys.executable,str(SCRIPT),str(source),"--output",str(target)],capture_output=True)
   self.assertEqual(first.returncode,0,first.stderr);before=target.read_bytes()
   second=subprocess.run([sys.executable,str(SCRIPT),str(source),"--output",str(target)],capture_output=True)
   self.assertNotEqual(second.returncode,0);self.assertEqual(target.read_bytes(),before)

 def test_consumed_restart_has_no_restart_action(self):
  r=module.triage({"error":"runtime read/execute validation failed (os error 32)","restarts_attempted":1})
  self.assertNotIn("coordinate_one_authorized_cold_restart",r["next_actions"])
  self.assertTrue(r["stop_restarting"])
 def test_direct_runtime_failure_is_classified(self):
  r=module.triage({"error":"runtime read/execute validation failed (os error 32)"})
  self.assertEqual(r["classification"],"runtime_acl_sharing_violation")
 def test_capture_only_requested_failure(self):
  r=module.triage({"error":"FrameArrived timed out","required_capabilities":["capture"],"checks":{"import":"PASS","windows":"PASS","capture":"FAIL"}})
  self.assertEqual(r["status"],"BLOCKED")
  self.assertEqual(r["requested_checks"]["capture"],"FAIL")
 def test_context_and_nested_invalid_required(self):
  r=module.triage({"error":"FrameArrived timed out","desired_mode":"elevated","observed_mode":"unelevated","restoration_state":"PENDING","checks":{"input":"PASS","capture":"FAIL"}})
  self.assertTrue(r["temporary_mode"])
  self.assertEqual(r["restoration_state"],"PENDING")
  for e in [{"required_capabilities":[[]]},{"restoration_state":"secret arbitrary value"}]:
   with self.assertRaises(ValueError):module.triage(e)

if __name__=="__main__":unittest.main()
