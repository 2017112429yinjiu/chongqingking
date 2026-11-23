$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
& $engine --headless --path $project --script "$PSScriptRoot/original_apron.gd" -- "--art-profile=$PSScriptRoot/../candidate.json" $PSScriptRoot
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b "$PSScriptRoot/../city_and_windows.blend" --python-exit-code 2 -P "$PSScriptRoot/author.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $blender -b "$PSScriptRoot/city_and_market_steps.blend" --python-exit-code 2 -P "$PSScriptRoot/check_source.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& $engine --headless --path $project --editor --import
exit $LASTEXITCODE
