$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$python=Join-Path $work 'tools/blender-4.3.2-windows-x64/4.3/python/bin/python.exe'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$previous=Join-Path $work 'scene_r24/window_life/front_steps/city_and_market_steps.blend'
& $blender -b $previous --python-exit-code 2 -P "$PSScriptRoot/author.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $python "$PSScriptRoot/editor_base.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b --python-exit-code 2 -P "$PSScriptRoot/editor_local.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b "$PSScriptRoot/city_and_lane_connections.blend" --python-exit-code 2 -P "$PSScriptRoot/check_source.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $engine --headless --path $project --editor --import
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& "$PSScriptRoot/verify.ps1" -Phase junction
exit $LASTEXITCODE
