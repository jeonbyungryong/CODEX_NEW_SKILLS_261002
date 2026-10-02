---
name: verify-powershell-handoff
description: Use when preparing or reviewing Windows PowerShell file-validation handoffs, especially JSON manifests, native helpers, Unicode paths or a different author and user shell. Not for browser connection repair or general Git publication.
---

# Verify a PowerShell handoff

Check behavior in the recipient's actual engine and invocation, not just the author's shell. Record the engine/version, script encoding, working directory and input contract. Do not upgrade the user's environment to make an unverified script pass.

## JSON collection shape comes before the loop

Windows PowerShell 5.1 can emit a parsed JSON array as one pipeline object. Therefore `@(Get-Content ... | ConvertFrom-Json)` can have Count 1 for several records. An outer `@()` does not guarantee the intended record collection.

For a known nonempty array of non-null records, separate parsing from collection construction:

```powershell
$parsed = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 |
    ConvertFrom-Json -ErrorAction Stop
$items = @($parsed)
if ($items.Count -ne $expectedCount) { throw 'Unexpected item count' }
```

This is not a universal JSON normalizer: empty arrays and null entries need explicit handling. If zero records or null preservation matters, validate the original JSON and retain the array as an object property:

```powershell
$raw = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 -ErrorAction Stop
$null = ConvertFrom-Json -InputObject $raw -ErrorAction Stop
$text = $raw.Trim()
if (-not ($text.StartsWith('[') -and $text.EndsWith(']'))) {
    throw 'Expected a JSON array'
}
$envelope = ConvertFrom-Json -InputObject ('{"records":' + $text + '}') -ErrorAction Stop
$items = $envelope.records
if ($items -isnot [array]) { throw 'Expected an array property' }
if ($items.Count -ne $expectedCount) { throw 'Unexpected item count' }
```

Assert count AND per-record type/required fields in the target engine. Test 0, 1 and several records, malformed JSON and null entries as relevant. Reject invalid records under the schema; do not silently drop nulls, flatten nested data or relax the count to hide incompatibility.

## Native calls and text are separate boundaries

Use an argument array and splatting, never a joined command string. Verify the helper's received argument count and exact Unicode/space-containing values. Capture the native exit code immediately after each invocation, before another native command; check its documented success meaning. Invocation errors and nonzero exits must prevent success.

Specify JSON decoding, script encoding and log encoding independently. Windows PowerShell 5.1 needs a suitable script encoding (UTF-8 BOM for Unicode source); UTF-8 log writing cannot repair incorrectly decoded helper output. Use a new log or verify its existing encoding.

## Evidence required for readiness

Run the actual entry point under the recipient's shell, with representative inputs and a deliberate failing case. If execution is unavailable, provide precise blocking tests instead of claiming READY.

Report separately: syntax/hash checks; collection/argument/runtime checks; remaining untested behavior. A parser, source hash or a different wrapper's ASCII success is not full handoff validation. This Skill grants no installs, external writes or permission changes.
