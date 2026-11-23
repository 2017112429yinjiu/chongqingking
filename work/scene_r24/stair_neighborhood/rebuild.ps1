param()
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$prior=Join-Path $work 'scene_r24/street_photo_study/city_and_street_use.blend'
$source=Join-Path $PSScriptRoot 'city_and_neighborhood.blend'
$library=Join-Path $work 'project/chongqing_blender_v05/scanned_assets/prepared_assets.blend'
foreach ($task in @(
    @($prior,'author.py'), @($source,'tree_feet.py'), @($source,'tree_inventory.py'),
    @($library,'tree_distances.py'), @($source,'span_exposure.py')
)) {
    & $blender -b $task[0] --python-exit-code 2 -P (Join-Path $PSScriptRoot $task[1])
    if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
}
& $engine --path $project --headless --editor --import
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot 'bake_walk_lanes.gd') -- "--art-profile=$PSScriptRoot/candidate.json" $PSScriptRoot
if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
& (Join-Path $PSScriptRoot 'verify.ps1') -Phase contact
exit $LASTEXITCODE

