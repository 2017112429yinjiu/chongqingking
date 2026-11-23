param([ValidateSet('before','candidate','final','perf','perf_before','walk','market','delivery','smoke')][string]$Phase='final')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$baseline=Join-Path $PSScriptRoot 'build11_profile.json'
$candidate=Join-Path $PSScriptRoot 'candidate_profile.json'
$names='r24_west_seam,r24_center_seam,r24_stall,r24_repair,r23_main_road,r24_canopy_joint,r23_shop_window,r24_counter'
if ($Phase -in @('before','candidate','final')){
  if ($Phase -ne 'before') {$names+=',r24_market_ground,r24_west_doorstep'}
  $options=@('--capture','--capture-size=1280x720','--settle-frames=25',"--capture-view=$names","--capture-dir=$PSScriptRoot/$Phase")
  if ($Phase -eq 'before') {$options+="--art-profile=$baseline"}
  if ($Phase -eq 'candidate') {$options+="--art-profile=$candidate"}
  & $engine --path $project --position 2600,120 -- @options
} elseif ($Phase.StartsWith('perf')){
  $options=@("--qa-dir=res://verification_r24/build12/$Phase",'--perf-views=r24_west_seam,r24_stall')
  if ($Phase -eq 'perf_before') {$options+="--art-profile=$baseline"}
  & $engine --path $project --position 2600,120 --disable-vsync --script (Join-Path $work 'performance_1080_r23.gd') -- @options
} elseif ($Phase -eq 'walk'){
  & $engine --path $project --headless --fixed-fps 60 --script (Join-Path $PSScriptRoot '../city_frame_11864101/walk_seams.gd') -- "--qa-dir=res://verification_r24/build12"
} else {
  $test=if($Phase -eq 'market'){'walk'}else{$Phase}
  & (Join-Path $work 'verify_frontage_r24.ps1') -Phase $test -Run build12
}
exit $LASTEXITCODE

