# Windows report CLI compatibility

This local MIT-licensed patch extends the pinned Cloudflare Security Audit
validators. Upstream source attribution and LICENSE remain in the installed
package. `bundle.json` records each original base hash, reviewed replacement
hash and canonical local file; the lock records both upstream and overlay
provenance. An upstream change to a patched file stops sync for review.

Both normal commands work on Windows 10/11 with built-in Windows PowerShell 5.1
and Node 22+:

```text
node <skill>/validate-findings.cjs <findings.json>
node <skill>/validate-coverage-ledger.cjs <coverage-ledger.json>
```

The Windows branch uses a trusted fixed PowerShell bootstrap (no profiles,
interpolation of input, policy changes, downloads or external services).
It compiles the small checked-in C# reader using the built-in .NET runtime. Paths arrive as JSON on
stdin. Win32 CreateFileW opens reparse points themselves; disk-file/type and
attribute checks reject links, directories and special files. Ancestor handles
remain open with no write/delete sharing while reading. Only local disks and
ordinary file paths are accepted: UNC/network drives, device namespaces, DOS
devices, alternate data streams and ambiguous names are rejected before open.
Unicode local filenames are supported.

The reader enforces 5 MiB and a four-second process timeout; fatal UTF-8,
schema, nesting, cardinality, diagnostic sanitization and semantic checks remain
in the existing validators. The POSIX reader is unchanged. This does not provide
the OS sandbox required for executing untrusted audit targets.

API references:
[CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew),
[GetFileType](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletype),
[GetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle).
