$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$city=Join-Path $work 'scene_r24/courtyard_life/kitchen/city_and_courtyard.blend'
foreach ($task in @(@($city,'author.py'),@((Join-Path $PSScriptRoot 'city_and_rooms.blend'),'wall_finish.py'),@((Join-Path $PSScriptRoot 'city_and_windows.blend'),'check_source.py'))) {
    & $blender -b $task[0] --python-exit-code 2 -P (Join-Path $PSScriptRoot $task[1])
    if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
}
$project=Join-Path $work 'project/chongqing_godot_v05'
& $engine --headless --path $project --editor --import
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
$folder=Join-Path $PSScriptRoot 'perf'
& $engine --headless --path $project --script (Join-Path $folder 'bake.gd') -- "--art-profile=$PSScriptRoot/pre_visibility_profile.json" $folder
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
Copy-Item -LiteralPath (Join-Path $folder 'interior_wall_faces.res') -Destination (Join-Path $project 'assets/rooms_r24/interior_wall_faces.res') -Force
