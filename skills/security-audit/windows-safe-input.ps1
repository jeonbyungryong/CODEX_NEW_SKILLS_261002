# Local Windows compatibility patch. MIT; upstream attribution is preserved.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
try {
  # Pin built-ins: Windows PowerShell otherwise scans third-party module trees
  # on first cmdlet discovery, which can exceed the bounded reader lifetime.
  $env:PSModulePath = $PSHOME + '\Modules'
  Import-Module ($env:PSModulePath + '\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
  $request = [Console]::In.ReadToEnd() | ConvertFrom-Json
  Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class AuditBoundedFile {
  [StructLayout(LayoutKind.Sequential)]
  struct Info {
    public uint Attr;
    public System.Runtime.InteropServices.ComTypes.FILETIME Creation, Access, Write;
    public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
  }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr sa, uint mode, uint flags, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool GetFileInformationByHandle(SafeFileHandle file, out Info info);
  [DllImport("kernel32.dll")] static extern uint GetFileType(SafeFileHandle file);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] static extern uint GetDriveTypeW(string root);
  static SafeFileHandle Open(string name, bool directory) {
    // OPEN_REPARSE_POINT opens the link itself; BACKUP_SEMANTICS also permits
    // directory handles. Deny write/delete sharing while inspecting/reading.
    var h = CreateFileW("\\\\?\\" + name, directory ? 0x80u : 0x80000000u, 1, IntPtr.Zero, 3, 0x02200000, IntPtr.Zero);
    if (h.IsInvalid) { h.Dispose(); throw new IOException("input could not be opened or read safely"); }
    try {
      Info info;
      if (GetFileType(h) != 1 || !GetFileInformationByHandle(h, out info)) throw new IOException("input must be a regular file");
      if ((info.Attr & 0x400) != 0) throw new IOException("input must not be a symlink or reparse point");
      if (((info.Attr & 0x10) != 0) != directory) throw new IOException("input must be a regular file");
      return h;
    } catch { h.Dispose(); throw; }
  }
  public static byte[] Read(string name, int limit) {
    if (limit < 1 || limit > 5242880 || name.Length < 3 || name[1] != ':' || name[2] != '\\') throw new IOException("input must be a safe local file path");
    var drive = GetDriveTypeW(name.Substring(0, 3));
    if (drive != 2 && drive != 3 && drive != 6) throw new IOException("input must be a safe local file path");
    var parents = new List<SafeFileHandle>();
    try {
      // Keep every ancestor pinned so a checked directory cannot be renamed
      // into a junction between checking it and opening its child.
      parents.Add(Open(name.Substring(0, 3), true));
      for (int i = 3; i < name.Length; i++) if (name[i] == '\\') parents.Add(Open(name.Substring(0, i), true));
      using (var handle = Open(name, false)) {
        Info info;
        if (!GetFileInformationByHandle(handle, out info)) throw new IOException("input could not be opened or read safely");
        if ((((ulong)info.SizeHigh << 32) | info.SizeLow) > (ulong)limit) throw new IOException("input exceeds " + limit + " byte limit");
        using (var stream = new FileStream(handle, FileAccess.Read, 65536, false))
        using (var output = new MemoryStream()) {
          byte[] buffer = new byte[65536];
          int n;
          while ((n = stream.Read(buffer, 0, Math.Min(buffer.Length, limit + 1 - (int)output.Length))) > 0) {
            output.Write(buffer, 0, n);
            if (output.Length > limit) throw new IOException("input exceeds " + limit + " byte limit");
          }
          return output.ToArray();
        }
      }
    } finally { foreach (var h in parents) h.Dispose(); }
  }
}
'@
  $data = [AuditBoundedFile]::Read([string]$request.path, [int]$request.limit)
  [Console]::WriteLine((@{ok=$true; data=[Convert]::ToBase64String($data)} | ConvertTo-Json -Compress))
} catch {
  $message = $_.Exception.GetBaseException().Message
  if ($message -notmatch '^input (must be a (safe local file path|regular file)|must not be a symlink or reparse point|exceeds [0-9]+ byte limit)$') {
    $message = 'input could not be opened or read safely'
  }
  [Console]::WriteLine((@{ok=$false; reason=$message} | ConvertTo-Json -Compress))
}
