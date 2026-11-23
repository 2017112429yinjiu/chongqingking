param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run)
$ErrorActionPreference='Stop'
$game=(Resolve-Path (Join-Path $PSScriptRoot '../../project/chongqing_godot_v05')).Path
$engine=(Resolve-Path (Join-Path $PSScriptRoot '../../tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe')).Path
$base="verification_r24/indoor_delivery/$Run"
if(Test-Path -LiteralPath (Join-Path $game $base)){throw "Evidence directory already exists"}
function Run-Game([string]$name,[string]$script,[string[]]$Extra=@(),[bool]$draw=$false){
    $rel="$base/$name"
    $dir=Join-Path $game $rel
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $display=if($draw){@('--resolution','960x540')}else{@('--headless')}
    $argsForGame=@($display)+@('--path',$game,'--fixed-fps','60','--log-file',(Join-Path $dir 'engine.log'))
    if($script){$argsForGame+=@('--script',(Join-Path $PSScriptRoot $script))}
    $argsForGame+=@('--','--day-one-test','--qa-still-frames',"--qa-dir=res://$rel")+$Extra
    & $engine @argsForGame *> (Join-Path $dir 'console.log')
    if($LASTEXITCODE -ne 0 -or (Select-String -Path (Join-Path $dir 'engine.log') -Pattern '^(ERROR|SCRIPT ERROR|SHADER ERROR):' -Quiet)){throw "Inspect $dir"}
}
Run-Game 'teaching' 'verify_shift.gd' @() $true
Run-Game 'views' 'views.gd' @() $true
Run-Game 'both_entrances' 'crossing.gd' @() $true
Run-Game 'free_order' 'free_order.gd' @("--checkpoints=res://$base/teaching") $true
Run-Game 'wait_rejoin' 'verify_shift.gd' @('--test-roadblock','--test-dismount','--test-look-away')
Run-Game 'restore' 'resume.gd' @("--checkpoints=res://$base/teaching")
Run-Game 'practice' 'practice.gd' @('--practice-unit')
Run-Game 'old_saves' '../road_and_shift/resume.gd'
Run-Game 'driving' '' @('--r17-delivery-test')
Run-Game 'interactions' '' @('--r16-test')
Run-Game 'smoke' '' @('--smoke-test')
