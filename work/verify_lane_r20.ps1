param([ValidateSet('import','capture','comparison','street','lane','gameplay','delivery','survey','performance','court_performance')][string]$Phase='capture',[string]$Run='current')
$ErrorActionPreference='Stop'
if ($Phase -eq 'court_performance' -and $Run -eq 'current') {$Run='resident_court_gpu'}
if ($Run -notmatch '^[A-Za-z0-9_-]+$') {throw 'Invalid evidence name'}
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$outDir="verification_r20/$Run"
$logDir=Join-Path $project "$outDir/logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$qa="--qa-dir=res://$outDir"
$argsForPhase=switch ($Phase) {
 'import' { @('--headless','--editor','--import') }
 'capture' { @('--','--capture','--capture-size=1600x900','--settle-frames=90','--capture-view=narrow_passage,r20_notices,r20_reverse,r20_tap,r20_laundry,r20_tree_court,r20_neighbor,r20_seated_neighbor,noodle_corner,central_steps,r18_workstation,r16_meter',"--capture-dir=res://$outDir/captures") }
 'street' { @('--headless','--fixed-fps','60','--','--r19-street-test',$qa) }
 'lane' { @('--headless','--fixed-fps','60','--','--r20-lane-test',$qa) }
 'gameplay' { @('--headless','--fixed-fps','60','--','--r16-test',$qa) }
 'delivery' { @('--headless','--fixed-fps','60','--','--r17-delivery-test',$qa) }
 'survey' { @('--headless','--fixed-fps','60','--','--survey-test',"--test-report=res://$outDir/survey.json") }
 'performance' { @('--','--r16-performance','--perf-views=street_entry,central_steps,noodle_corner,west_lane,narrow_passage,r18_rider_active',$qa) }
 'court_performance' { @('--','--r16-performance','--perf-views=r20_tree_court,r20_neighbor,r20_seated_neighbor',$qa) }
 'comparison' {
     $compareDir=Join-Path $project 'verification_r20/resident_meter_comparison'
     New-Item -ItemType Directory -Force -Path $compareDir | Out-Null
     $profile=Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $project 'assets/render_profile_r20.json') | ConvertFrom-Json
     $profile.meter_lod=$false
     $json=$profile | ConvertTo-Json -Depth 32
     [IO.File]::WriteAllText((Join-Path $compareDir 'comparison_profile.json'),$json,[Text.UTF8Encoding]::new($false))
     @('--','--capture','--capture-size=1600x900','--settle-frames=90','--capture-view=r16_meter,noodle_corner,narrow_passage,r20_tree_court','--art-profile=res://verification_r20/resident_meter_comparison/comparison_profile.json','--capture-dir=res://verification_r20/resident_meter_comparison/comparison_captures')
 }
}
$log=Join-Path $logDir "$Phase.log"
& $engine --path $project --log-file $log @argsForPhase *> (Join-Path $logDir "$Phase.console.txt")
if ($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:|Parse Error:' -Quiet)) {throw "$Phase failed; see $log"}
Write-Output "$Phase passed"
