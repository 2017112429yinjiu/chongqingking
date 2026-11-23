$ErrorActionPreference='Stop'
$p=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$gpu=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$dir=Join-Path $p 'verification_r20/resident_ab'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$profile=Get-Content -LiteralPath (Join-Path $p 'assets/render_profile_r20.json') -Raw -Encoding utf8 | ConvertFrom-Json
$profile.court_resident=$false
[IO.File]::WriteAllText((Join-Path $dir 'disabled.json'),($profile|ConvertTo-Json -Depth 32),[Text.UTF8Encoding]::new($false))
foreach($take in @('off_a','on','off_b')){
    $condition=if($take -eq 'on'){'res://assets/render_profile_r20.json'}else{'res://verification_r20/resident_ab/disabled.json'}
    $dest=Join-Path $dir $take
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $log=Join-Path $dest 'engine.log'
    & $gpu --path $p --log-file $log -- --r16-performance "--art-profile=$condition" '--perf-views=r20_tree_court,r20_seated_neighbor,r18_rider_active' "--qa-dir=res://verification_r20/resident_ab/$take" *> (Join-Path $dest 'console.txt')
    if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:' -Quiet)){throw "$take failed"}
    Write-Output "$take measured"
}
