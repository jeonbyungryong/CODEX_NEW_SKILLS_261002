param(
    [Parameter(Mandatory=$true)][string]$HelperPython,
    [Parameter(Mandatory=$true)][string]$EvidenceDirectory
)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $EvidenceDirectory) { throw 'Evidence directory already exists' }
$null = New-Item -ItemType Directory -Path $EvidenceDirectory
$results = New-Object System.Collections.Generic.List[object]
function Assert-Test([string]$Name, [bool]$Condition) {
    if (-not $Condition) { throw "FAIL: $Name" }
    $results.Add([pscustomobject]@{name=$Name;pass=$true})
}
function Read-RecordArray([string]$Raw) {
    $null = ConvertFrom-Json -InputObject $Raw -ErrorAction Stop
    $text = $Raw.Trim()
    if (-not ($text.StartsWith('[') -and $text.EndsWith(']'))) { throw 'Expected JSON array' }
    $envelope = ConvertFrom-Json -InputObject ('{"records":' + $text + '}') -ErrorAction Stop
    $items = $envelope.records
    if ($items -isnot [array]) { throw 'Expected array property' }
    # Return envelope, not the array through the function's output pipeline.
    return $envelope
}
foreach ($case in @(
    @{name='empty array';raw='[]';count=0},
    @{name='singleton';raw='[{"path":"one"}]';count=1},
    @{name='three records';raw='[{"path":"one"},{"path":"two"},{"path":"three"}]';count=3},
    @{name='null retained';raw='[null]';count=1},
    @{name='nested retained';raw='[["one","two"]]';count=1}
)) {
    $parsed = Read-RecordArray $case.raw
    Assert-Test $case.name ($parsed.records.Count -eq $case.count)
    if ($case.name -eq 'null retained') {
        Assert-Test 'null not silently dropped' ($null -eq $parsed.records[0])
    }
    if ($case.name -eq 'nested retained') {
        Assert-Test 'nested not flattened' ($parsed.records[0] -is [array] -and $parsed.records[0].Count -eq 2)
    }
}
foreach ($invalid in @('{"path":"not-array"}','null','[{"path":}]')) {
    $rejected = $false
    try { $null = Read-RecordArray $invalid } catch { $rejected = $true }
    Assert-Test ("reject " + $invalid) $rejected
}
$normal = '[{"path":"one"},{"path":"two"},{"path":"three"}]'
$control = @(ConvertFrom-Json -InputObject $normal)
$expectedControl = if ($PSVersionTable.PSVersion.Major -eq 5) { 1 } else { 3 }
Assert-Test 'historical direct-pipeline shape reproduced' ($control.Count -eq $expectedControl)
$parsed = ConvertFrom-Json -InputObject $normal
$items = @($parsed)
Assert-Test 'assignment normal nonempty shape' ($items.Count -eq 3)
# Unicode literals assembled to keep this harness ASCII-source compatible.
$word = -join ([char[]]@(0xAC80,0xD1A0))
$label = -join ([char[]]@(0xC124,0xCE58,0x20,0xD655,0xC778))
$inputPath = 'D:\' + $word + ' folder\slide one.png'
$probe = Join-Path $PSScriptRoot 'native-probe.py'
$priorEncoding = [Console]::OutputEncoding
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $ErrorActionPreference = 'Continue'
    $nativeArgs = @($probe,'--input',$inputPath,'--label',$label)
    $LASTEXITCODE = $null
    $output = @(& $HelperPython @nativeArgs 2>&1)
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    Assert-Test 'native zero exit captured' ($code -eq 0)
    $received = ($output -join [Environment]::NewLine) | ConvertFrom-Json
    Assert-Test 'native argument boundaries and unicode' (
        $received.Count -eq 4 -and $received[0] -ceq '--input' -and
        $received[1] -ceq $inputPath -and $received[2] -ceq '--label' -and
        $received[3] -ceq $label
    )
    $log = Join-Path $EvidenceDirectory 'probe.log'
    $output | Out-File -LiteralPath $log -Encoding UTF8 -ErrorAction Stop
    $roundTrip = Get-Content -LiteralPath $log -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Test 'UTF8 log unicode roundtrip' ($roundTrip[1] -ceq $inputPath -and $roundTrip[3] -ceq $label)
    $ErrorActionPreference = 'Continue'
    $failureArgs = @($probe,'--input',$inputPath,'--label','FAIL')
    $LASTEXITCODE = $null
    $failureOutput = @(& $HelperPython @failureArgs 2>&1)
    $failureCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    Assert-Test 'native nonzero exit captured' ($failureCode -eq 7)
    $ready = $false
    try {
        if ($null -eq $failureCode -or $failureCode -ne 0) { throw 'Helper failed' }
        $ready = $true
    } catch {}
    Assert-Test 'nonzero cannot reach readiness' (-not $ready)
} finally {
    [Console]::OutputEncoding = $priorEncoding
}
$receipt = [pscustomobject]@{
    engine=$PSVersionTable.PSVersion.ToString()
    tests=$results.Count
    failures=0
    controlCount=$control.Count
    checks=$results.ToArray()
    limit='Synthetic native argv/exit/log probe, not a production helper or complete publication workflow'
}
$receipt | ConvertTo-Json -Depth 5 | Out-File -LiteralPath (Join-Path $EvidenceDirectory 'result.json') -Encoding UTF8
$receipt | ConvertTo-Json -Depth 5
