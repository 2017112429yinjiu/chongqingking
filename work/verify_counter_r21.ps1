param([ValidateSet('import','character','gameplay','delivery','survey','performance','capture','movie','probe','lane')][string]$Phase='capture',
      [string]$Run='current')
$ErrorActionPreference='Stop'
if ($Run -notmatch '^[a-zA-Z0-9_-]+$') {throw 'Invalid run directory'}
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$relative="verification_r21/$Run"
$evidence=Join-Path $project $relative
$logDir=Join-Path $evidence 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$qa="--qa-dir=res://$relative"
$take=Join-Path $PSScriptRoot 'capture_counter_take.gd'
$argsForPhase=switch ($Phase){
 'import' {@('--headless','--editor','--import')}
 'character' {@('--headless','--fixed-fps','60','--','--r18-shopkeeper-test',$qa)}
 'gameplay' {@('--headless','--fixed-fps','60','--','--r16-test',$qa)}
 'delivery' {@('--headless','--fixed-fps','60','--','--r17-delivery-test',$qa)}
 'lane' {@('--headless','--fixed-fps','60','--','--r20-lane-test',$qa)}
 'survey' {@('--headless','--fixed-fps','60','--','--survey-test',"--test-report=res://$relative/survey.json")}
 'capture' {@('--','--capture','--capture-size=1600x900','--settle-frames=45','--capture-view=r18_idle,r18_lift,r18_place,r18_player_eye,r18_face,r18_grip,r18_workstation,noodle_corner',"--capture-dir=res://$relative/captures")}
 'performance' {@('--','--r16-performance','--perf-views=r18_workstation,r18_player_eye,r18_face,noodle_corner',$qa)}
 'probe' {@('--headless','--fixed-fps','30','--script',$take,'--',$qa)}
 'movie' {@('--resolution','1280x720','--fixed-fps','30','--write-movie',(Join-Path $PSScriptRoot "scene_r21/$Run.avi"),'--script',$take,'--',$qa)}
}
$log=Join-Path $logDir "$Phase.log"
& $engine --path $project --log-file $log @argsForPhase *> (Join-Path $logDir "$Phase.console.txt")
if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:|Parse Error:' -Quiet)){throw "$Phase failed. See $log"}
Write-Output "$Phase passed for $Run"
