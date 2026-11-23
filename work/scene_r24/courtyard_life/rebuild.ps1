param([string]$Python = (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'))
$ErrorActionPreference='Stop'
$study=$PSScriptRoot
$work=(Resolve-Path (Join-Path $study '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$godot=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$prior=Join-Path $work 'scene_r24/stair_neighborhood/city_and_neighborhood.blend'
function Run-Checked ($exe,[string[]]$arguments) {
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) {throw "Build step failed ($LASTEXITCODE): $exe $arguments"}
}
function Blender-Script ($file,$script,[string[]]$extra=@()) {
    $arguments=@('-b')
    if ($file) {$arguments+=$file}
    $arguments+=@('--python-exit-code','2','-P',(Join-Path $study $script))
    if ($extra) {$arguments+=@('--')+$extra}
    Run-Checked $blender $arguments
}
Blender-Script $prior 'window_survey.py'
foreach ($script in @('board_print.py','plaster_map.py')) {
    Run-Checked $Python @((Join-Path $study $script))
}
foreach ($role in @('red','black','greens')) {
    Blender-Script '' 'bake_activity.py' @($role)
}
Blender-Script $prior 'author_city.py'
Blender-Script (Join-Path $work 'scene_r23/commuter_walk.blend') 'bake_standing.py'
Blender-Script (Join-Path $study 'city_and_courtyard.blend') 'paving/author.py'
Blender-Script (Join-Path $study 'greens.blend') 'kitchen/measure_clearance.py' @('prior_clearance.json')
Blender-Script '' 'bake_activity.py' @('--kitchen-fit','greens')
Blender-Script (Join-Path $study 'paving/city_and_courtyard.blend') 'kitchen/author.py'
Blender-Script (Join-Path $study 'kitchen/greens.blend') 'kitchen/measure_clearance.py' @('final_clearance.json')
Blender-Script (Join-Path $study 'kitchen/city_and_courtyard.blend') 'paving/check_source.py'
Run-Checked $godot @('--headless','--path',$project,'--editor','--import')
Run-Checked $godot @('--headless','--path',$project,'--script',(Join-Path $study 'wait_library.gd'))
Run-Checked $godot @('--headless','--path',$project,'--fixed-fps','60','--script',(Join-Path $study 'bake_returns.gd'),'--',"--art-profile=$study/pre_stance_profile.json",$study)
Run-Checked $godot @('--headless','--path',$project,'--editor','--import')
