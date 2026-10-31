// Local Windows compatibility patch. MIT; see third_party/security-audit/LICENSE.
'use strict';
const path = require('node:path');
const fs = require('node:fs');
const {spawnSync} = require('node:child_process');
const {TextDecoder} = require('node:util');

module.exports = function readWindowsInput(file, limit) {
  const unsafe = () => { throw new Error('input must be a safe local file path'); };
  if (typeof file !== 'string' || /[\x00-\x1f\x7f]/.test(file) || /^[\\/]{2}/.test(file)) unsafe();
  const full = path.win32.resolve(file);
  if (!/^[a-z]:\\/i.test(full) || full.slice(2).includes(':')) unsafe();
  const reserved = /^(con|prn|aux|nul|clock\$|conin\$|conout\$|com[1-9¹²³]|lpt[1-9¹²³])(?:\.|$)/iu;
  if (file.split(/[\\/]/).some(p => p !== '.' && p !== '..' && /[. ]$/.test(p)) ||
      full.slice(3).split('\\').some(p => reserved.test(p) || /[. ]$/.test(p))) unsafe();
  if (!Number.isInteger(limit) || limit < 1 || limit > 5 * 1024 * 1024) throw new Error('invalid input limit');
  const systemRoot = process.env.SystemRoot || process.env.WINDIR;
  if (!systemRoot || !path.win32.isAbsolute(systemRoot)) throw new Error('Windows reader unavailable');
  const powershell = path.join(systemRoot, 'System32/WindowsPowerShell/v1.0/powershell.exe');
  const env = {SystemRoot: systemRoot, WINDIR: systemRoot};
  for (const key of ['TEMP', 'TMP']) if (process.env[key]) env[key] = process.env[key];
  const bootstrap = fs.readFileSync(path.join(__dirname, 'windows-safe-input.ps1'), 'utf8');
  const r = spawnSync(powershell, ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command', bootstrap], {
    input: JSON.stringify({path:full, limit}), encoding:'utf8', windowsHide:true,
    timeout:4000, maxBuffer:8 * 1024 * 1024, env,
  });
  if (r.error || r.status !== 0) throw new Error('input could not be opened or read safely');
  let reply;
  try { reply = JSON.parse(r.stdout.replace(/^\uFEFF/, '')); }
  catch { throw new Error('Windows reader returned an invalid response'); }
  if (!reply.ok) throw new Error(reply.reason);
  const bytes = Buffer.from(reply.data, 'base64');
  if (bytes.length > limit) throw new Error(`input exceeds ${limit} byte limit`);
  try { return new TextDecoder('utf-8', {fatal:true, ignoreBOM:true}).decode(bytes); }
  catch { throw new Error('input is not valid UTF-8'); }
};
