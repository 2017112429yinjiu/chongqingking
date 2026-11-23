param([ValidateSet('before','trial','current','walk','market','delivery','performance','smoke','contact','window720','window1080')][string]$Phase='current')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$qa='res://verification_r24/build13'
if ($Phase -in @('before','trial','current')) {
 $views='r24_court_gap,r24_center_seam,r24_court_entry,r24_west_life,r24_lane_life,r23_main_road,r24_market_ground,r24_wire_anchor,r24_chess,r24_wire_fixing'
 $options=@('--capture','--capture-size=1280x720','--settle-frames=25',"--capture-view=$views","--capture-dir=$PSScriptRoot/$Phase")
 if ($Phase -eq 'before') {$options+="--art-profile=$PSScriptRoot/before.json"}
 if ($Phase -eq 'trial') {$options+="--art-profile=$PSScriptRoot/candidate.json"}
 & $engine --path $project --position 2600,120 -- @options
} elseif ($Phase -eq 'walk') {
 & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot '../city_frame_11864101/walk_seams.gd') -- "--qa-dir=$qa"
} elseif ($Phase -eq 'contact'){
 & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot 'audit.gd') -- "--qa-dir=$qa" "--study=$PSScriptRoot"
} elseif ($Phase -in @('window720','window1080')) {
 $resolution=if ($Phase -eq 'window720'){'1280x720'}else{'1920x1080'}
 $result=if ($Phase -eq 'window720'){$qa}else{"$qa/window_1080"}
 & $engine --path $project --position 40,45 --resolution $resolution --disable-vsync --script (Join-Path $PSScriptRoot 'performance_walk.gd') -- "--qa-dir=$result"
} elseif ($Phase -eq 'performance'){
 & $engine --path $project --position 2600,120 --disable-vsync --script (Join-Path $work 'performance_1080_r23.gd') -- "--qa-dir=$qa/gpu" '--perf-views=r24_center_seam,r23_main_road'
} else {
 $check=if($Phase -eq 'market'){'walk'}else{$Phase}
 & (Join-Path $work 'verify_frontage_r24.ps1') -Phase $check -Run build13
}
exit $LASTEXITCODE

