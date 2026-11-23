param(
    [string]$Run = ("local_" + (Get-Date -Format "yyyyMMdd_HHmmssfff")),
    [switch]$Graphics
)
$ErrorActionPreference = "Stop"
$work = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$game = Join-Path $work "project/chongqing_godot_v05"
$engine = Join-Path $work "tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe"
if ($Run -notmatch '^[\w-]+$') { throw "Use a short run name without path separators." }
$destination = Join-Path $game "verification_r24/road_shift/$Run"
if (Test-Path -LiteralPath $destination) { throw "This run already has evidence. Choose a new run name." }
New-Item -ItemType Directory -Path $destination | Out-Null
function Check-Scene([string]$name,[string]$script,[string[]]$options=@(),[bool]$draw=$false) {
    $directory = Join-Path $destination $name
    New-Item -ItemType Directory -Path $directory | Out-Null
    $resource = "res://verification_r24/road_shift/$Run/$name"
    [string[]]$display = if ($draw) { @("--resolution","960x540") } else { @("--headless") }
    [string[]]$arguments = @($display) + @("--path",$game,"--fixed-fps","60","--script",(Join-Path $PSScriptRoot $script),"--log-file",(Join-Path $directory "engine.log"),"--","--day-one-test","--qa-still-frames","--qa-dir=$resource") + $options
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $engine @arguments
        if ($LASTEXITCODE -ne 0) { throw "$name failed. See $directory" }
        if (-not (Test-Path -LiteralPath (Join-Path $directory "engine.log"))) { throw "$name produced no isolated run log." }
    } finally { Pop-Location }
}
Check-Scene "three_orders" "verify_shift.gd" @() $Graphics.IsPresent
Check-Scene "interrupted" "verify_shift.gd" @("--test-roadblock","--test-dismount","--test-look-away")
Check-Scene "old_obstruction" "crossing.gd" @("--former")
Check-Scene "stone_flight" "crossing.gd"
Check-Scene "court_crossing" "crossing.gd" @("--cross-court")
Check-Scene "court_descent" "crossing.gd" @("--down-court")
Check-Scene "lip_sizes" "lips.gd" @() $Graphics.IsPresent
Check-Scene "restore" "resume.gd"
Check-Scene "court_sections" "court.gd" @() $Graphics.IsPresent
