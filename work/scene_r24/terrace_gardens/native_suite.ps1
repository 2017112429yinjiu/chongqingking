param([Parameter(Mandatory)][string]$Run)
$ErrorActionPreference="Stop"
if ($Run -notmatch '^[a-zA-Z0-9_-]+$'){throw "Invalid run name"}
$work=(Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$game=Join-Path $work "project/chongqing_godot_v05"
$engine=Join-Path $work "tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe"
$root="verification_r24/terrace_gardens/$Run"
$destination=Join-Path $game $root
if(Test-Path -LiteralPath $destination){throw "Existing evidence"}
New-Item -ItemType Directory -Path $destination | Out-Null
function Run-Native([string]$script,[string]$name,[string[]]$flags=@(),[bool]$draw=$false){
 $out=Join-Path $destination $name
 New-Item -ItemType Directory -Path $out | Out-Null
 $entry=Join-Path (Split-Path $PSScriptRoot) $script
 $display=if($draw){@("--resolution","960x540")}else{@("--headless")}
 $arguments=@($display)+@("--path",$game,"--fixed-fps","60","--script",$entry,"--log-file",(Join-Path $out "engine.log"),"--","--day-one-test","--qa-still-frames","--qa-dir=res://$root/$name")+$flags
 & $engine @arguments *> (Join-Path $out "console.log")
 if($LASTEXITCODE -ne 0){throw "$name exited $LASTEXITCODE"}
 if(Select-String -Path (Join-Path $out "engine.log") -Pattern '^(SCRIPT ERROR|SHADER ERROR|ERROR):' -Quiet){throw "$name logged a runtime error"}
}
Run-Native "terrace_gardens/probe.gd" "slope"
Run-Native "terrace_gardens/north_contact.gd" "north_source"
Run-Native "district_age/parking.gd" "parked"
Run-Native "district_age/audit.gd" "ground"
foreach($i in 0..2){
 Run-Native "district_age/drive_matrix.gd" ("out"+$i) @("--batch=$i")
 Run-Native "district_age/drive_matrix.gd" ("back"+$i) @("--batch=$i","--reverse")
}
Run-Native "road_and_shift/verify_shift.gd" "three_orders"
Run-Native "terrace_gardens/east_ride.gd" "toe"
Run-Native "terrace_gardens/north_ride.gd" "north"
Run-Native "terrace_gardens/walk.gd" "walk" @() $true
Run-Native "terrace_gardens/roots.gd" "roots" @() $true
Run-Native "terrace_gardens/views.gd" "views" @() $true
