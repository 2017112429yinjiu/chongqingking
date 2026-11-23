param([ValidateSet('inlets','junction','steps','views','motion','timing','rooms','contacts','life','turns','seams','paving','market','delivery','smoke','street')][string]$Phase='inlets')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$profile=Join-Path $PSScriptRoot 'candidate.json'
$qa='res://verification_r24/build17b'
$art=@()
if((Get-FileHash $profile).Hash -ne (Get-FileHash (Join-Path $project 'assets/render_profile_r24.json')).Hash){$art+="--art-profile=$profile"}
$views='r24_east_upper_joint,r24_east_upper_reverse,r24_east_upper_grate,r24_east_inlet_0,r24_east_inlet_1,r24_market_steps_front,r24_main_tea_window'
switch ($Phase) {
 'inlets' { & $engine --headless --path $project --fixed-fps 60 --script "$PSScriptRoot/test.gd" -- @art "--qa-dir=$qa" }
 'junction' { & $engine --headless --path $project --fixed-fps 60 --script "$PSScriptRoot/../test.gd" -- @art "--qa-dir=$qa" }
 'steps' { $market=Join-Path $work 'scene_r24/window_life/front_steps'; & $engine --headless --path $project --fixed-fps 60 --script "$market/test.gd" -- @art "--qa-dir=$qa" $market }
 'views' { & $engine --path $project --position 2600,110 -- --capture --capture-size=1198x720 "--capture-view=$views" "--capture-dir=$PSScriptRoot/current" @art }
 'motion' { & $engine --path $project --position 2600,110 --resolution 960x540 --fixed-fps 60 --script "$PSScriptRoot/../walk.gd" -- @art "$PSScriptRoot/motion" }
 'timing' { & $engine --path $project --position 2600,110 --resolution 1198x720 --disable-vsync --script "$PSScriptRoot/../walk.gd" -- @art --timing "$PSScriptRoot/timing" }
 default { & "$work/scene_r24/window_life/verify.ps1" -Phase $Phase -Run build17b -Views $views -StudyDir $PSScriptRoot -Profile $profile }
}
exit $LASTEXITCODE
