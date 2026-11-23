param([Parameter(Mandatory)][string]$Run)
$ErrorActionPreference="Stop"
if($Run -notmatch '^[a-zA-Z0-9_-]+$'){throw "Invalid run name"}
$work=(Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$game=Join-Path $work "project/chongqing_godot_v05"
$engine=Join-Path $work "tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe"
$rel="verification_r24/terrace_gardens/$Run"
$folder=Join-Path $game $rel
if(Test-Path $folder){throw "Existing evidence"}
New-Item -ItemType Directory -Path $folder | Out-Null
$views="r24_yard20_fork_shoulder,r24_terrace21_lane_gardens,r24_terrace21_garden_walk"
Push-Location -LiteralPath $game
try{
 $argv="--path . --resolution 1280x720 --disable-vsync --max-fps 0 --script ../../scene_r24/road_and_shift/performance.gd --log-file $rel/engine.log -- --day-one-test --viewport-gpu --perf-views=$views --qa-dir=res://$rel"
 $p=Start-Process -WindowStyle Hidden -FilePath $engine -ArgumentList $argv -WorkingDirectory $game -PassThru -Wait
 if($p.ExitCode -ne 0 -or -not (Test-Path (Join-Path $folder "performance.json"))){throw "Timing failed"}
}finally{Pop-Location}
