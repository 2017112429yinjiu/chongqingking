param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run,[switch]$Timing)
$ErrorActionPreference='Stop'
$game=(Resolve-Path (Join-Path $PSScriptRoot '../../project/chongqing_godot_v05')).Path
$engine=(Resolve-Path (Join-Path $PSScriptRoot '../../tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe')).Path
$base="verification_r24/lunch_run/$Run"
if(Test-Path -LiteralPath (Join-Path $game $base)){throw "Use a new run name to preserve previous captures."}

function Test-Trip([string]$name,[string]$script,[string[]]$flags,[bool]$graphics=$false) {
    $rel="$base/$name"
    $dir=Join-Path $game $rel
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    $display=if($graphics){@('--resolution','960x540','--position','2600,90','--disable-vsync')}else{@('--headless')}
    $options=@($display)+@('--path',$game,'--log-file',(Join-Path $dir 'engine.log'))
    if($script -ne 'timing.gd'){$options+=@('--fixed-fps','60')}
    $options+=@('--script',(Join-Path $PSScriptRoot $script),'--','--day-one-test','--qa-still-frames',"--qa-dir=res://$rel")+$flags
    & $engine @options *> (Join-Path $dir 'console.log')
    if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath (Join-Path $dir 'engine.log') -Pattern '^(SCRIPT ERROR|SHADER ERROR|ERROR):' -Quiet)){throw "Inspect $dir"}
}
Test-Trip 'court_first' 'verify.gd' @('--practice-lunch') $true
Test-Trip 'homes_first' 'verify.gd' @('--practice-lunch','--homes-first') $true
Test-Trip 'loaded_ride' 'verify.gd' @('--practice-lunch','--scooter') $true
Test-Trip 'reopen' 'verify.gd' @("--restart=res://$base/court_first/two_paid.cfg")
Test-Trip 'next_order' 'verify.gd' @("--restart=res://$base/court_first/lunch.cfg",'--finished')
Test-Trip 'teacher' '../indoor_delivery/verify_shift.gd' @()
Test-Trip 'single' '../indoor_delivery/free_order.gd' @("--checkpoints=res://$base/teacher")
if($Timing){Test-Trip 'counter_timing' 'timing.gd' @('--practice-lunch') $true}
