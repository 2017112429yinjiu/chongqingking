param(
    [string]$Run = ("local_" + (Get-Date -Format "yyyyMMdd_HHmmssfff")),
    [string]$Python = "python",
    [switch]$Graphics,
    [switch]$FirstShift,
    [switch]$Timing
)
$ErrorActionPreference = "Stop"
if ($Run -notmatch '^[A-Za-z0-9_-]+$') { throw "Choose a new run name using letters, digits, hyphen or underscore." }
$work = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$game = Join-Path $work "project/chongqing_godot_v05"
$engine = Join-Path $work "tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe"
$blender = Join-Path $work "tools/blender-4.3.2-windows-x64/blender.exe"
$source = Join-Path $PSScriptRoot "city_and_yards.blend"
$qa = Join-Path $game "verification_r24/district_age"
if (Get-ChildItem -LiteralPath $qa -Directory | Where-Object { $_.Name.StartsWith($Run+"_") }) { throw "That run already has evidence." }
$logs = New-Item -ItemType Directory -Path (Join-Path $qa ($Run+"_source"))
function Inspect-Source([string]$script) {
    & $blender -b $source --python-exit-code 7 -P (Join-Path $PSScriptRoot ($script+".py")) *> (Join-Path $logs.FullName ($script+".log"))
    if ($LASTEXITCODE -ne 0) { throw "Blender failed in $script" }
}
Inspect-Source "reopen"
Inspect-Source "survey"
Inspect-Source "median_scan"
& $Python (Join-Path $PSScriptRoot "survey_queries.py")
if ($LASTEXITCODE -ne 0) { throw "Route preparation failed" }
foreach ($file in 'source_check.json','road_queries.json','median_sections.json','median_open_pixels.json','views.json') {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination $logs.FullName
}
& $engine --headless --path $game --editor --import --log-file (Join-Path $logs.FullName "import.log")
if ($LASTEXITCODE -ne 0) { throw "Godot import failed" }
function Native([string]$script,[string]$name,[string[]]$extra=@(),[bool]$draw=$false) {
    $resource = "verification_r24/district_age/"+$Run+"_"+$name
    $folder = New-Item -ItemType Directory -Path (Join-Path $game $resource)
    [string[]]$display=if ($draw) { @("--resolution","960x540") } else { @("--headless") }
    $argv = @("--path",$game,"--fixed-fps","60","--script",(Join-Path $PSScriptRoot $script),"--log-file",(Join-Path $folder.FullName "engine.log"))+$display+@("--","--day-one-test","--qa-still-frames",("--qa-dir=res://"+$resource))+$extra
    & $engine @argv
    if ($LASTEXITCODE -ne 0) { throw "Godot failed in $name" }
}
Native "audit.gd" "ground"
foreach ($i in 0..2) {
    Native "drive_matrix.gd" ("out"+$i) @(("--batch="+$i))
    Native "drive_matrix.gd" ("back"+$i) @(("--batch="+$i),"--reverse")
}
Native "parking.gd" "parked"
Native "ride.gd" "west_up" @("--west-entry")
Native "ride.gd" "west_down" @("--west-entry","--reverse")
Native "ride.gd" "east_up" @("--east_bypass")
Native "ride.gd" "east_down" @("--east_bypass","--reverse")
Native "ride.gd" "blue_up" @("--corner_bypass")
Native "ride.gd" "blue_down" @("--corner_bypass","--reverse")
if ($Graphics) {
    Native "walkthrough.gd" "views" @() $true
    Native "motion.gd" "walk" @() $true
}
& $Python (Join-Path $PSScriptRoot "road_report.py") $Run
if ($LASTEXITCODE -ne 0) { throw "A road or contact check failed. Preserve the run." }
if ($FirstShift) { & (Join-Path $PSScriptRoot "../road_and_shift/verify.ps1") -Run $Run -Graphics:$Graphics }
if ($Timing) {
    $resource="verification_r24/district_age/"+$Run+"_timing"
    $folder=New-Item -ItemType Directory -Path (Join-Path $game $resource)
    $views="r24_yard20_shelter_from_lane,r24_yard20_wall_1413081560,r24_yard20_blue_bend_reverse"
    & $engine --path $game --resolution 1280x720 --disable-vsync --log-file (Join-Path $folder.FullName "engine.log") --script (Join-Path $PSScriptRoot "../road_and_shift/performance.gd") -- --day-one-test "--qa-dir=res://$resource" "--perf-views=$views" --viewport-gpu
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $folder.FullName "performance.json"))) { throw "Graphics timing failed." }
}
