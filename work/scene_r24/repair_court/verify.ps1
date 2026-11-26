param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run,[switch]$Capture)
$ErrorActionPreference='Stop'
$root=(Resolve-Path "$PSScriptRoot/../../..").Path
$game=Join-Path $root 'work/project/chongqing_godot_v05'
$godot=Join-Path $root 'work/tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$blender=Join-Path $root 'work/tools/blender-4.3.2-windows-x64/blender.exe'
$out=New-Item -ItemType Directory (Join-Path $root ".cloud-dev/plot0/$Run")
$oldApp=$env:APPDATA
$oldQA=$env:CQ_QA_DIR
try {
    $env:APPDATA=(New-Item -ItemType Directory (Join-Path $root ('.cloud-dev/u'+[guid]::NewGuid().ToString('N').Substring(0,8)))).FullName
    function Run-Case([string]$name,[string]$exe,[array]$options) {
        $env:CQ_QA_DIR=(New-Item -ItemType Directory (Join-Path $out.FullName $name)).FullName
        $log=Join-Path $env:CQ_QA_DIR 'console.log'
        & $exe @options *> $log
        if ($LASTEXITCODE -or (Select-String -LiteralPath $log -Pattern '^(ERROR:|SCRIPT ERROR:|SHADER ERROR:|Traceback )' -Quiet)) {
            throw "Inspect $log"
        }
    }
    $district=Join-Path $PSScriptRoot '../district_500'
    Run-Case compose $blender @('-b',"$PSScriptRoot/../district_patrol/city_and_patrol.blend",'--python-exit-code','8','-P',"$district/compose.py")
    Run-Case source $blender @('-b',"$district/city_and_outer.local.blend",'--python-exit-code','8','-P',"$PSScriptRoot/audit.py")
    Run-Case import $godot @('--headless','--editor','--import','--path',$game)
    $engineFlags=@('--path',$game,'--fixed-fps','60')
    $flags=@('--','--explore-500','--repair-court','--day-one-test','--qa-still-frames')
    $display=@('--resolution','1152x648','--disable-vsync')
    $mode=if ($Capture) {$display} else {@('--headless')}
    Run-Case walk $godot (@($mode)+$engineFlags+@('--script',"$PSScriptRoot/walk.gd")+$flags)
    $walk=Get-Content -Raw -Encoding utf8 (Join-Path $env:CQ_QA_DIR 'walk.json') | ConvertFrom-Json
    if ($walk.checks.Count -ne 10 -or @($walk.checks | Where-Object { -not $_.pass }).Count) {throw 'Incomplete walk'}
    if ($Capture) {
        if ($walk.images -lt 2 -or $walk.images -ne @(Get-ChildItem "$env:CQ_QA_DIR/walk_*.jpg").Count) {throw 'Missing native frames'}
        Run-Case views $godot ($display+$engineFlags+@('--script',"$PSScriptRoot/views.gd")+$flags)
        foreach ($view in 'street','court','group','workbench','courtyard_entry','street_eye') {
            if (-not (Test-Path "$env:CQ_QA_DIR/$view.png")) {throw "Missing $view"}
        }
    }
    Write-Output $out.FullName
} finally {
    $env:APPDATA=$oldApp
    $env:CQ_QA_DIR=$oldQA
}
