// Cold-start regression: synthetic local JSON only; no secrets or target code.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
if(process.platform!=='win32')process.exit(0);
console.log({node:process.version,platform:process.platform});
const root=process.env.SystemRoot;
const exe=path.join(root,'System32/WindowsPowerShell/v1.0/powershell.exe');
const env={SystemRoot:root,WINDIR:root,TEMP:process.env.TEMP,TMP:process.env.TMP,
  PSModulePath:path.join(path.dirname(exe),'Modules')};
function probe(name,code,input){
  const start=Date.now();
  const r=spawnSync(exe,['-NoLogo','-NoProfile','-NonInteractive','-Command',code],{input,encoding:'utf8',env,windowsHide:true,timeout:20000,maxBuffer:1024*1024});
  console.log(JSON.stringify({name,elapsed:Date.now()-start,status:r.status,error:r.error?.code,stderr:r.stderr,stdout:r.stdout}));
  if(r.error || r.status!==0 || Date.now()-start>=10000 || !JSON.parse(r.stdout).ok) throw new Error('Windows cold-start reader failed');
}
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'audit-probe-'));
try{
  const file=path.join(dir,'report.json');fs.writeFileSync(file,'[]');
  let code=fs.readFileSync(path.resolve(__dirname,'../../skills/security-audit/windows-safe-input.ps1'),'utf8');
  code="[Console]::Error.WriteLine('bootstrap');\n"+code;
  code=code.replace('  $request = [Console]::In.ReadToEnd() | ConvertFrom-Json',"  $raw = [Console]::In.ReadToEnd(); [Console]::Error.WriteLine('stdin read'); $request = $raw | ConvertFrom-Json");
  code=code.replace('  Add-Type',"  [Console]::Error.WriteLine('input parsed');\n  Add-Type");
  code=code.replace("'@\n", "'@\n  [Console]::Error.WriteLine('compiled');\n");
  code=code.replace('  [Console]::WriteLine((@{ok=$true;',"  [Console]::Error.WriteLine('file read');\n  [Console]::WriteLine((@{ok=$true;");
  probe('native-reader',code,JSON.stringify({path:file,limit:5242880}));
}finally{fs.rmSync(dir,{recursive:true,force:true});}
