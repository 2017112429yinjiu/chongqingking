param([string]$Label='pair_a')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
foreach($variant in 'before','current'){
 $options=@("--qa-dir=res://verification_r24/build12/$Label/$variant",'--perf-views=r24_west_seam,r24_stall')
 if ($variant -eq 'before') {$options+="--art-profile=$PSScriptRoot/build11_profile.json"}
 & $engine --path $project --position 2600,120 --disable-vsync --script (Join-Path $work 'performance_1080_r23.gd') -- @options *> (Join-Path $PSScriptRoot "$($Label)_$variant.log")
 if ($LASTEXITCODE -ne 0) {exit $LASTEXITCODE}
}

