$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$blender=Join-Path $PSScriptRoot 'tools/blender-4.3.2-windows-x64/blender.exe'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$script=Join-Path $PSScriptRoot 'capture_court_resident.gd'
$log=Join-Path $PSScriptRoot 'audit/court_resident_movie.log'
$movie=Join-Path $PSScriptRoot 'audit/court_resident.avi'
& $engine --path $project --resolution 1280x720 --fixed-fps 30 --write-movie $movie --log-file $log --script $script *> (Join-Path $PSScriptRoot 'audit/court_resident_movie.console.txt')
if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:' -Quiet)){throw 'Court take failed'}
& $blender -b --python-exit-code 2 -P (Join-Path $PSScriptRoot 'encode_court_take.py') *> (Join-Path $PSScriptRoot 'audit/court_resident_encode.log')
if($LASTEXITCODE -ne 0){throw 'Court take encoding failed'}
