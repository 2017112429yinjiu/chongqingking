$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$project=Join-Path $work 'project/chongqing_godot_v05'
$previous=Join-Path $PSScriptRoot '../candidate.json'
$sets=@(@('baseline720','1280x720',$previous),@('current720','1280x720',"$PSScriptRoot/candidate.json"),@('current1080','1920x1080',"$PSScriptRoot/candidate.json"),@('baseline1080','1920x1080',$previous))
foreach($run in $sets){
    $dir=Join-Path $PSScriptRoot ('perf/'+$run[0])
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $sample=$null
    $monitor=Get-Command nvidia-smi -ErrorAction SilentlyContinue
    try {
        if($monitor){$sample=Start-Process -FilePath $monitor.Source -ArgumentList @('--query-gpu=timestamp,utilization.gpu,temperature.gpu,power.draw,clocks.current.graphics,memory.used','--format=csv','-l','1') -RedirectStandardOutput (Join-Path $dir 'device.csv') -WindowStyle Hidden -PassThru}
        & $engine --path $project --position 40,45 --resolution $run[1] --disable-vsync --script "$PSScriptRoot/../walk.gd" -- --timing "--art-profile=$($run[2])" $dir *> "$dir/play.log"
        if($LASTEXITCODE -ne 0){throw "Route failed in $dir"}
    } finally {if($sample -and -not $sample.HasExited){$sample.Kill();$sample.WaitForExit()}}
}
