param([ValidateSet('import','gameplay','delivery','character','lab','capture','performance','rider','rider_physics')][string]$Phase='character')
$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$logDir=Join-Path $project 'verification_r18/logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$engineArgs=switch($Phase){
 'import' { @('--headless','--editor','--import') }
 'gameplay' { @('--headless','--fixed-fps','60','--','--r16-test') }
 'delivery' { @('--headless','--fixed-fps','60','--','--r17-delivery-test') }
 'character' { @('--headless','--fixed-fps','60','--','--r18-shopkeeper-test') }
 'rider' { @('--fixed-fps','60','--','--r18-rider-test') }
 'rider_physics' { @('--headless','--fixed-fps','60','--','--r18-rider-test') }
 'lab' { @('--script','res://scripts/qa_character_art.gd') }
 'performance' { @('--','--r16-performance') }
 'capture' { @('--','--capture','--capture-view=r18_idle,r18_reach,r18_lift,r18_place,r18_workstation,r18_player_eye,r18_greet,r18_face,r18_grip','--art-profile=res://assets/render_profile_r18.json','--capture-size=1600x900','--settle-frames=36','--capture-dir=res://verification_r18/city_current') }
}
$log=Join-Path $logDir ($Phase+'.log')
& $engine --path $project --log-file $log @engineArgs *> (Join-Path $logDir ($Phase+'.console.txt'))
if($LASTEXITCODE -ne 0){throw "$Phase exited $LASTEXITCODE; see $log"}
if(Select-String -LiteralPath $log -Pattern 'SCRIPT ERROR:|Parse Error:|^ERROR:' -Quiet){throw "$Phase logged engine errors; see $log"}
Write-Output "$Phase completed without engine errors"
