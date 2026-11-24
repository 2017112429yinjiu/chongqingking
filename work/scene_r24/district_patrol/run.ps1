param([string]$Run,[string]$Script='patrol.gd',[switch]$Draw,[string[]]$Extra)
$ErrorActionPreference='Stop'
$game=(Resolve-Path "$PSScriptRoot/../../project/chongqing_godot_v05").Path
$exe=(Resolve-Path "$PSScriptRoot/../../tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe").Path
$folder="verification_r24/district_patrol/$Run"
$dest=Join-Path $game $folder
if(Test-Path -LiteralPath $dest){throw 'Use a new run name'}
New-Item -ItemType Directory -Path $dest | Out-Null
$mode=@(if($Draw){'--resolution','1000x564','--position','40,40','--disable-vsync'}else{'--headless'})
& $exe @mode --path $game --fixed-fps 60 --log-file "$dest/engine.log" --script (Join-Path $PSScriptRoot $Script) -- --day-one-test --qa-still-frames "--qa-dir=res://$folder" @Extra *> "$dest/console.log"
exit $LASTEXITCODE
