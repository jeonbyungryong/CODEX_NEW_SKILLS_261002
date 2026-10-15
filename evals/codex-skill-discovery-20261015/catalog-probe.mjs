// Temporary read-only client for the installed Codex app-server.
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';

const [binary, ...cwds] = process.argv.slice(2);
if (!binary || !cwds.length) throw new Error('Expected binary and cwd arguments');
const proc = spawn(binary, ['app-server', '--stdio'], {
  windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'],
});
const pending = new Map();
let sequence = 0;
let stderr = '';
proc.stderr.on('data', data => { stderr += data.toString(); });
proc.on('error', error => {
  for (const entry of pending.values()) entry.reject(error);
});
proc.on('exit', code => {
  for (const entry of pending.values()) {
    clearTimeout(entry.timer);
    entry.reject(new Error(`Proxy exited: ${code}`));
  }
});
const lines = createInterface({ input: proc.stdout });
lines.on('line', line => {
  let message;
  try { message = JSON.parse(line); } catch { return; }
  if (!pending.has(message.id)) return;
  const entry = pending.get(message.id);
  pending.delete(message.id);
  clearTimeout(entry.timer);
  if (message.error) entry.reject(new Error(JSON.stringify(message.error)));
  else entry.resolve(message.result);
});
function rpc(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`Timed out: ${method}`));
    }, 15000);
    pending.set(id, { resolve, reject, timer });
    proc.stdin.write(JSON.stringify({ id, method, params }) + '\n');
  });
}
const names = new Set([
  'specify-failure-recovery', 'review-release-evidence',
  'coordinate-device-validation', 'verify-powershell-handoff',
  'diagnose-computer-use-recovery',
]);
try {
  const init = await rpc('initialize', {
    clientInfo: { name: 'temporary_skill_discovery_probe', version: '2026.10.15' },
    capabilities: { experimentalApi: true },
  });
  proc.stdin.write(JSON.stringify({ method: 'initialized', params: {} }) + '\n');
  const result = await rpc('skills/list', { cwds, forceReload: true });
  console.log(JSON.stringify({
    platformFamily: init.platformFamily, platformOs: init.platformOs,
    data: result.data.map(entry => ({
      cwd: entry.cwd,
      totalSkills: entry.skills.length,
      skills: entry.skills.map((skill, index) => ({ ...skill, catalogIndex: index }))
        .filter(skill => names.has(skill.name)),
      errors: entry.errors,
    })),
  }, null, 2));
} catch (error) {
  console.error(JSON.stringify({ error: error.message, stderr }));
  process.exitCode = 1;
} finally {
  proc.stdin.end();
  lines.close();
  // Stop only this script's child stdio server, never the desktop app/server.
  proc.kill();
}
