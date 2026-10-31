const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const skill = path.resolve(__dirname, '../../skills/security-audit');

test('both report CLIs accept ordinary JSON on this platform', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'audit Windows 한글 '));
  try {
    const input = path.join(temp, '한글 보고서.json');
    fs.writeFileSync(input, '[]');
    for (const script of ['validate-findings.cjs', 'validate-coverage-ledger.cjs']) {
      const r = spawnSync(process.execPath, [path.join(skill, script), input], {encoding:'utf8', timeout:15000});
      assert.equal(r.status, 0, r.stderr || String(r.error));
      assert.match(r.stdout, /PASS:/);
    }
  } finally { fs.rmSync(temp, {recursive:true, force:true}); }
});

test('Windows native reader rejects unsafe paths without opening them', {skip:process.platform !== 'win32'}, () => {
  const read = require(path.join(skill, 'windows-safe-input.cjs'));
  for (const input of ['NUL', 'CON', '\\\\.\\pipe\\audit-test', '\\\\server\\share\\report.json', 'C:\\report.json:secret', 'C:\\missing.\\a.json']) {
    assert.throws(() => read(input, 5242880), /safe local file path/);
  }
});

test('Windows reader rejects directories and ancestor/leaf junctions', {skip:process.platform !== 'win32'}, () => {
  const read = require(path.join(skill, 'windows-safe-input.cjs'));
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'audit-links-'));
  try {
    fs.mkdirSync(path.join(temp, 'target'));
    fs.writeFileSync(path.join(temp, 'target', 'report.json'), '[]');
    assert.throws(() => read(temp, 5242880), /regular file/);
    fs.symlinkSync(path.join(temp, 'target'), path.join(temp, 'junction'), 'junction');
    assert.throws(() => read(path.join(temp, 'junction', 'report.json'), 5242880), /symlink|reparse/);
    // Junctions require no developer-mode symlink privilege and exercise a leaf reparse point too.
    assert.throws(() => read(path.join(temp, 'junction'), 5242880), /symlink|reparse/);
  } finally { fs.rmSync(temp, {recursive:true, force:true}); }
});
