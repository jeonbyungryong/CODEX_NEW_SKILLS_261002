# PowerShell handoff evaluation

2026-10-02. Synthetic reviews; not product/device acceptance.

- [Frozen protocol](protocol.json): H1 same-input five control and five guided contexts; four single-sample holdouts.
- [Raw primary responses](responses.json), [shuffled independent grading](independent-review.md), [holdout responses](holdout-responses.json), [measurements and limits](measurements.json).
- [5.1 primitive results](runtime-51.json), [7 primitive results](runtime-7.json).
- [Reproducible primitive harness](Test-Handoff-Primitives.ps1) and [synthetic native helper](native-probe.py).

All evaluation agents inherited GPT-6.1 Sol / High; recorded trace had zero tools. The parent executed the local primitive harness separately. This does not prove the real file-validation helper or full production wrapper works.

To reproduce with existing local runtimes, invoke the harness via the exact engine, passing an absolute existing Python 3 executable and a new evidence directory:

```powershell
powershell.exe -NoProfile -File .\Test-Handoff-Primitives.ps1 -HelperPython '<existing python.exe>' -EvidenceDirectory '<new local evidence folder>'
pwsh.exe -NoProfile -File .\Test-Handoff-Primitives.ps1 -HelperPython '<existing python.exe>' -EvidenceDirectory '<another new local evidence folder>'
```

The harness creates only its new evidence directory and log/result files. It refuses an existing destination and temporarily sets/restores process console output encoding. It performs no uploads, real Git changes, device operations or installations. A supported Python 3 with stdout.reconfigure is required; none is installed by the harness. Do not reuse these counts as universal JSON/schema validation or browser recovery evidence.
