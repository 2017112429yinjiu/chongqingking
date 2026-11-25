param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run,[switch]$View)
$ErrorActionPreference='Stop'
$root=(Resolve-Path "$PSScriptRoot/../../..").Path
$engine=Join-Path $root 'work/tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$game=Join-Path $root 'work/project/chongqing_godot_v05'
$dest=Join-Path $PSScriptRoot "evidence/$Run"
if (Test-Path $dest) {throw "Choose a fresh survey name"}
$env:CQ_QA_DIR=(New-Item -ItemType Directory $dest).FullName
$private=New-Item -ItemType Directory (Join-Path $root ".cloud-dev/outer-neighborhood/$Run") -Force
$env:APPDATA=$private.FullName
[string[]]$mode=@('--headless')
if ($View.IsPresent) { $mode=@('--resolution','1060x620','--disable-vsync') }
& $engine @mode --path $game --fixed-fps 60 --log-file "$dest/engine.log" --script "$PSScriptRoot/survey.gd" -- --day-one-test --qa-still-frames *> "$dest/console.log"
exit $LASTEXITCODE
