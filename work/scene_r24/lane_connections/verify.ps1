param([ValidateSet('junction','steps','views','motion','timing','rooms','contacts','life','turns','seams','paving','market','delivery','smoke','street')][string]$Phase='junction')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$windows=Join-Path $work 'scene_r24/window_life'
$views='r24_east_upper_joint,r24_east_upper_grate,r24_east_upper_reverse,r24_market_steps_front,r24_main_tea_window'
$qa='res://verification_r24/build17'
$art=@()
$profile=Join-Path $PSScriptRoot 'candidate.json'
if((Get-FileHash $profile).Hash -ne (Get-FileHash (Join-Path $project 'assets/render_profile_r24.json')).Hash){$art+="--art-profile=$profile"}
switch ($Phase) {
 'junction' { & $engine --path $project --headless --fixed-fps 60 --script "$PSScriptRoot/test.gd" -- @art "--qa-dir=$qa" }
 'steps' { & $engine --path $project --headless --fixed-fps 60 --script "$windows/front_steps/test.gd" -- @art "--qa-dir=$qa" "$windows/front_steps" }
 'views' { & $engine --path $project --position 2600,110 -- --capture --capture-size=1198x720 "--capture-view=$views" "--capture-dir=$PSScriptRoot/current" @art }
 'motion' { & $engine --path $project --position 2600,110 --resolution 960x540 --fixed-fps 60 --script "$PSScriptRoot/walk.gd" -- @art "$PSScriptRoot/motion" }
 'timing' { & $engine --path $project --position 2600,110 --resolution 1198x720 --disable-vsync --script "$PSScriptRoot/walk.gd" -- @art --timing "$PSScriptRoot/timing" }
 default { & "$windows/verify.ps1" -Phase $Phase -Run build17 -Views $views -StudyDir $PSScriptRoot -Profile "$PSScriptRoot/candidate.json" }
}
exit $LASTEXITCODE
