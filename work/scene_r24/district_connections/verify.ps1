param([ValidateSet('build','import','source','connections','walk','motion','views','before','timing','prior_timing','regressions','editor')][string]$Phase='connections',[string]$Run='build18')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$blender=Join-Path $work 'tools/blender-4.3.2-windows-x64/blender.exe'
$profile=Join-Path $PSScriptRoot 'candidate.json'
$qa="res://verification_r24/$Run"
$art=@()
if((Get-FileHash $profile).Hash -ne (Get-FileHash (Join-Path $project 'assets/render_profile_r24.json')).Hash){$art+="--art-profile=$profile"}
$views='r24_join18_long,r24_join18_bend,r24_join18_road,r24_join18_alley,r24_join18_court,r24_join18_shop,r24_join18_room,r24_join18_front,r24_join18_threshold,r24_join18_prep'
switch ($Phase) {
 'build' { & $blender -b "$work/scene_r24/lane_connections/side_inlets/city_and_inlets.blend" --python-exit-code 2 -P "$PSScriptRoot/author.py" }
 'import' { & $engine --headless --editor --path $project --import }
 'editor' { & $engine --headless --editor --path $project res://main.tscn --quit-after 100 }
 'source' { & $blender -b "$PSScriptRoot/city_and_connections.blend" --python-exit-code 2 -P "$PSScriptRoot/check_source.py" }
 'connections' { & $engine --log-file "$PSScriptRoot/connections_engine.log" --headless --path $project --fixed-fps 60 --script "$PSScriptRoot/test.gd" -- @art "--qa-dir=$qa" }
 'walk' { & $engine --log-file "$PSScriptRoot/walk_engine.log" --headless --path $project --fixed-fps 60 --script "$PSScriptRoot/walk_rooms.gd" -- --no-images @art "$project/verification_r24/$Run/walk" }
 'motion' { & $engine --path $project --position 2600,110 --resolution 960x540 --fixed-fps 60 --script "$PSScriptRoot/walk_rooms.gd" -- @art "$PSScriptRoot/motion" }
 {$_ -in @('views','before')} {
   $folder='current'
   if($Phase -eq 'before'){$art=@("--art-profile=$PSScriptRoot/before.json");$folder='prior_final'}
   & $engine --path $project --position 2600,110 -- --capture --capture-size=960x540 "--capture-view=$views" "--capture-dir=$PSScriptRoot/$folder" @art
 }
 {$_ -in @('timing','prior_timing')} {
   if($Phase -eq 'prior_timing'){$art=@("--art-profile=$PSScriptRoot/before.json")}
   & $engine --path $project --position 2600,110 --resolution 1198x720 --disable-vsync --script "$PSScriptRoot/shop_timing.gd" -- @art "$PSScriptRoot/$Phase"
 }
 'regressions' {
   $failures=@()
   foreach($test in @('rooms','contacts','life','turns','seams','paving','market','delivery','smoke','street')){
     & "$work/scene_r24/window_life/verify.ps1" -Phase $test -Run $Run -StudyDir $PSScriptRoot -Profile $profile *> "$PSScriptRoot/check_$test.log"
     if($LASTEXITCODE -ne 0){$failures+=$test}
   }
   foreach($item in @(@('inlets','lane_connections/side_inlets'),@('junction','lane_connections'),@('steps','window_life/front_steps'))){
     $folder=Join-Path $work ("scene_r24/"+$item[1])
     & $engine --headless --path $project --fixed-fps 60 --script "$folder/test.gd" -- @art "--qa-dir=$qa" $folder *> (Join-Path $PSScriptRoot ("check_"+$item[0]+".log"))
     if($LASTEXITCODE -ne 0){$failures+=$item[0]}
   }
   if($failures.Count -gt 0){throw ("Failed regression checks: "+($failures -join ", "))}
 }
}
exit $LASTEXITCODE
