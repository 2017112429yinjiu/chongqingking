param([ValidateSet('life','turns','paving','contacts','seams','market','street','delivery','smoke','views','before','west_take','court_take','window720','window1080')][string]$Phase='life')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$qa='res://verification_r24/build14'
$previous=Join-Path $work 'scene_r24/stair_neighborhood'
$views='r24_chess_table,r24_west_bowl,r24_west_threshold,r24_west_kitchen,r24_west_arrival,r24_west_life,r24_chess,r24_court_gap,r23_main_road'
switch ($Phase) {
 'paving' { & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot 'paving/test.gd') -- "--qa-dir=$qa" (Join-Path $PSScriptRoot 'paving') }
 'turns' { & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot 'turns.gd') -- "--qa-dir=$qa" }
 'life' { & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot 'audit.gd') -- "--qa-dir=$qa" $PSScriptRoot }
 'contacts' { & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $previous 'audit.gd') -- "--qa-dir=$qa" }
 'seams' { & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $work 'scene_r24/city_frame_11864101/walk_seams.gd') -- "--qa-dir=$qa" }
 'views' { & $engine --path $project --position 2600,120 -- --capture --capture-size=1280x720 --settle-frames=24 "--capture-view=$views" "--capture-dir=$PSScriptRoot/current" }
 'before' { & $engine --path $project --position 2600,120 -- --capture --capture-size=1280x720 --settle-frames=24 "--capture-view=$views" "--capture-dir=$PSScriptRoot/before_final" "--art-profile=$PSScriptRoot/before.json" }
 {$_ -in @('west_take','court_take')} {
   $mode=if ($Phase -eq 'court_take'){'--court'}else{'--west'}
   & $engine --path $project --position 2600,120 --resolution 960x540 --fixed-fps 60 --script (Join-Path $PSScriptRoot 'street_take.gd') -- $mode "$PSScriptRoot/$Phase"
 }
 {$_ -in @('window720','window1080')} {
   $resolution=if ($Phase -eq 'window720'){'1280x720'}else{'1920x1080'}
   & $engine --path $project --position 40,45 --resolution $resolution --disable-vsync --script (Join-Path $PSScriptRoot 'window_perf.gd') -- "--qa-dir=$qa/$Phase"
 }
 default {
   $test=if($Phase -eq 'market'){'walk'}else{$Phase}
   & (Join-Path $work 'verify_frontage_r24.ps1') -Phase $test -Run build14
 }
}
exit $LASTEXITCODE

