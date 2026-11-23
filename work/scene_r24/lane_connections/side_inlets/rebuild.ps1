$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$junction=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$out=Join-Path $project 'assets/lane_inlets_r24'
& $blender -b "$junction/city_and_lane_connections.blend" --python-exit-code 2 -P "$PSScriptRoot/author.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b --python-exit-code 2 -P "$junction/editor_local.py" -- $out
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b "$PSScriptRoot/city_and_inlets.blend" --python-exit-code 2 -P "$PSScriptRoot/check_source.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $engine --headless --editor --path $project --import
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& "$PSScriptRoot/verify.ps1" -Phase inlets
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& "$PSScriptRoot/verify.ps1" -Phase junction
exit $LASTEXITCODE
