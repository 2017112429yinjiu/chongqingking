param([ValidateSet('walk','views','gpu','gpu_prior')][string]$Phase='walk', [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Run='build17b')
$ErrorActionPreference='Stop'
$study=Join-Path $PSScriptRoot 'scene_r24/city_frame_11864101'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$evidence="res://verification_r24/$Run/city_frame"
switch ($Phase) {
  'walk' {
    & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $study 'walk_seams.gd') -- "--qa-dir=$evidence"
  }
  'views' {
    $list='r24_canopy_joint,r24_canopy_under,r24_hoop,r24_frame,r24_frame_walk,r24_step_edge,r24_west_seam,r24_center_seam,r24_lower_seam,r24_court_entry'
    & $engine --path $project --position 2600,120 -- --capture --capture-size=1280x720 --settle-frames=25 "--capture-view=$list" "--capture-dir=$evidence/final_views"
  }
  default {
    $variant=if ($Phase -eq 'gpu_prior') {'build10'} else {$Run}
    $arguments=@("--qa-dir=$evidence/gpu_$variant",'--perf-views=r24_frame,r24_canopy_joint')
    if ($Phase -eq 'gpu_prior') {$arguments+="--art-profile=$study/baseline_profile.json"}
    & $engine --path $project --position 2600,120 --disable-vsync --script (Join-Path $PSScriptRoot 'performance_1080_r23.gd') -- @arguments
  }
}
exit $LASTEXITCODE

