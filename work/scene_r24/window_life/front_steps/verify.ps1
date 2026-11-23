param([ValidateSet('steps','approach','rooms','contacts','life','turns','seams','paving','market','delivery','smoke','street','views','walk','window720','window1080')][string]$Phase='steps')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$proj=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$profile=Join-Path $PSScriptRoot 'candidate.json'
if ($Phase -in @('steps','approach')){
    $art=@()
    if ((Get-FileHash (Join-Path $proj 'assets/render_profile_r24.json')).Hash -ne (Get-FileHash $profile).Hash){$art+="--art-profile=$profile"}
    if ($Phase -eq 'steps'){
        & $engine --headless --fixed-fps 60 --path $proj --script "$PSScriptRoot/test.gd" -- @art --qa-dir=res://verification_r24/build16 $PSScriptRoot
    } else {
        & $engine --resolution 960x540 --position 2600,110 --fixed-fps 60 --path $proj --script "$PSScriptRoot/walk_market.gd" -- @art "$PSScriptRoot/route"
    }
} else {
    $views='r24_market_steps_front,r24_market_steps_along,r24_market_steps_upper,r24_main_tea_window,r24_main_supper_window,r24_west_pantry,r23_main_road,r24_west_kitchen'
    & "$PSScriptRoot/../verify.ps1" -Phase $Phase -Run build16 -Views $views -StudyDir $PSScriptRoot -Profile $profile
}
exit $LASTEXITCODE
