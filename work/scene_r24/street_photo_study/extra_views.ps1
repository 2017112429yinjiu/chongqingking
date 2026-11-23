$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
& $engine --path $project --position 2600,120 -- --capture --capture-size=1280x720 --settle-frames=25 --capture-view=r24_market_ground,r24_west_doorstep "--art-profile=$PSScriptRoot/before_views_profile.json" "--capture-dir=$PSScriptRoot/before_extra" *> (Join-Path $PSScriptRoot 'before_extra.log')
if ($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $engine --path $project --resolution 960x540 --position 2600,120 --fixed-fps 60 --script (Join-Path $PSScriptRoot 'walk_market_take.gd') -- "$PSScriptRoot/motion" *> (Join-Path $PSScriptRoot 'walk_take.log')
exit $LASTEXITCODE

