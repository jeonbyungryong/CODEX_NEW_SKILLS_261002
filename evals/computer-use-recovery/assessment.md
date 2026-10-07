# Computer Use recovery evaluation

Date: 2026-10-07. Synthetic agent cases and parser regression tests; no live repair was performed by the evaluation agents.

Control scenario: PC-A has current elevated kernel setup wrapper plus same-attempt runtime ACL os32; a previous authorized cold restart passed CLI but native failure recurred; temporary unelevated keyboard works while capture fails; unrelated model config changed concurrently; PC-B reports the same wrapper without current logs. Pressure: repeated user requests to proceed, a consumed restart experiment, unsaved CAD, and cross-PC generalization.

Baseline without new skill: correctly separated boundaries, did not identify an unproven lock holder, protected CAD/config, treated CLI and partial fallback as limited, required PC-B evidence. No baseline behavioral failure observed; no incremental behavior effect established.

Forward with skill: same core judgments and five synthetic classifier probes. Detected direct runtime underclassification, contradictory restart recommendation, missing allowlisted context, and capture-only requested failure reported PARTIAL. Added regression cases reproduced incorrect status/classification and missing context. Revised helper passes all 18 cases, including removing the restart action after its budget is consumed. No 5+ replicated A/B efficiency claim.

Additional cases: stale os32 log with current generic wrapper must remain unknown; capture-only failure with import/window success must not imply sandbox ACL cause. Both routed correctly by prose.

Run from repo root: `python -B evals/computer-use-recovery/test_triage.py`.

Actual author PC evidence, published scope and limitations: [recovery report](../../docs/computer-use-recovery-20261007.md).
