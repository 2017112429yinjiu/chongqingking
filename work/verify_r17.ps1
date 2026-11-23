param([ValidateSet('import','survey','capture','gameplay','performance','delivery','character')][string]$Phase='survey')
$ErrorActionPreference='Stop'
if(Select-String -LiteralPath (Join-Path $PSScriptRoot 'project/chongqing_godot_v05/scripts/shopkeeper.gd') -Pattern 'shopkeeper_r18.glb' -Quiet){throw 'This active project has moved to R18. Use verify_r18.ps1; preserve historical R17 reports.'}
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$logDir=Join-Path $project 'verification_r17/logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$argsForEngine=switch($Phase){
 'import' { @('--headless','--editor','--import') }
 'survey' { @('--headless','--fixed-fps','60','--','--survey-test','--test-report=res://verification_r17/survey_test.json') }
 'gameplay' { @('--headless','--fixed-fps','60','--','--r16-test') }
 'delivery' { @('--headless','--fixed-fps','60','--','--r17-delivery-test') }
 'character' { @('--headless','--fixed-fps','60','--','--r17-character-test') }
 'performance' { @('--','--r16-performance') }
 'capture' { @('--','--capture','--capture-view=r17_worker_entry,r17_worker_door,r17_A04_entry,r17_west_route,r17_east_route,r17_narrow_route,r16_shop,r17_shopkeeper,r17_serve,r17_takeaway,r16_meter','--art-profile=res://assets/render_profile_r17.json','--capture-size=1280x720','--settle-frames=24','--capture-dir=res://verification_r17/captures') }
}
$log=Join-Path $logDir ($Phase+'.log')
& $engine --path $project --log-file $log @argsForEngine *> (Join-Path $logDir ($Phase+'.console.txt'))
if($LASTEXITCODE -ne 0){throw "$Phase exited $LASTEXITCODE; see $log"}
if(Select-String -LiteralPath $log -Pattern 'SCRIPT ERROR:|Parse Error:|^ERROR:' -Quiet){throw "$Phase logged engine errors; see $log"}
Write-Output "$Phase completed without engine errors"
