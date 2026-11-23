$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$engine = Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$candidate = Join-Path $PSScriptRoot 'checkpoints/R16a_20261120/Godot'
$logDir = Join-Path $candidate 'verification_r16/logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
function Invoke-Check([string]$Name,[string[]]$Arguments) {
    Write-Output "Running $Name"
    $log = Join-Path $logDir ($Name + '.log')
    & $engine --path $candidate --log-file $log @Arguments *> (Join-Path $logDir ($Name + '.console.txt'))
    if ($LASTEXITCODE -ne 0) { throw "$Name failed; exit $LASTEXITCODE. See $log" }
    if (Select-String -LiteralPath $log -Pattern 'SCRIPT ERROR:|Parse Error:|^ERROR:' -Quiet) { throw "$Name logged an engine error: $log" }
    Write-Output "$Name passed"
}
Invoke-Check 'candidate_import' @('--headless','--editor','--import')
Invoke-Check 'candidate_gameplay' @('--headless','--','--r16-test')
Invoke-Check 'candidate_survey' @('--headless','--','--survey-test','--test-report=res://verification_r16/survey_test.json')
Invoke-Check 'candidate_capture' @('--','--capture','--capture-view=r16_scooter,r16_clothesline,r16_roof,r16_shop,r16_meter,street_entry,residential_entry,roofscape','--art-profile=res://assets/render_profile_r16.json','--capture-size=1280x720','--settle-frames=24','--capture-dir=res://verification_r16/captures')
Invoke-Check 'candidate_performance' @('--','--r16-performance')
Write-Output 'Candidate checks completed'
