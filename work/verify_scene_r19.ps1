param([ValidateSet('import','street','gameplay','delivery','survey','capture','performance','performance_baseline')][string]$Phase='street')
$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$logDir=Join-Path $project 'verification_r19/logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$engineArgs=switch($Phase){
 'import' { @('--headless','--editor','--import') }
 'street' { @('--headless','--fixed-fps','60','--','--r19-street-test','--qa-dir=res://verification_r19/current') }
 'gameplay' { @('--headless','--fixed-fps','60','--','--r16-test','--qa-dir=res://verification_r19/current') }
 'delivery' { @('--headless','--fixed-fps','60','--','--r17-delivery-test','--qa-dir=res://verification_r19/current') }
 'survey' { @('--headless','--fixed-fps','60','--','--survey-test','--test-report=res://verification_r19/current/survey.json') }
 'capture' { @('--','--capture','--capture-view=street_entry,noodle_corner,central_steps,west_lane,residential_entry,narrow_passage,r19_seating,r19_stair_detail,r18_workstation','--capture-size=1600x900','--settle-frames=90','--capture-dir=res://verification_r19/current/captures') }
 'performance' { @('--','--r16-performance','--perf-views=street_entry,central_steps,noodle_corner,west_lane,narrow_passage,r18_rider_active','--qa-dir=res://verification_r19/current') }
 'performance_baseline' { @('--','--r16-performance','--perf-views=street_entry,central_steps,noodle_corner,west_lane,narrow_passage,r18_rider_active','--art-profile=res://assets/render_profile_r18.json','--qa-dir=res://verification_r19/baseline_performance') }
}
$log=Join-Path $logDir ($Phase+'.log')
& $engine --path $project --log-file $log @engineArgs *> (Join-Path $logDir ($Phase+'.console.txt'))
if($LASTEXITCODE -ne 0){throw "$Phase exited $LASTEXITCODE; see $log"}
if(Select-String -LiteralPath $log -Pattern 'SCRIPT ERROR:|Parse Error:|^ERROR:' -Quiet){throw "$Phase logged engine errors; see $log"}
Write-Output "$Phase completed without engine errors"
