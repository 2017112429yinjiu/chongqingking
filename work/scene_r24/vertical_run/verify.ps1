param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run,[switch]$Timing)
$ErrorActionPreference='Stop'
$game=(Resolve-Path (Join-Path $PSScriptRoot '../../project/chongqing_godot_v05')).Path
$engine=(Resolve-Path (Join-Path $PSScriptRoot '../../tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe')).Path
$base="verification_r24/vertical_run/$Run"
if(Test-Path -LiteralPath (Join-Path $game $base)){throw "Choose a fresh evidence directory."}
function Run-Case([string]$label,[string]$script,[string[]]$flags,[bool]$draw=$false){
    $location="$base/$label"
    $dir=Join-Path $game $location
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    $video=if($draw){@('--resolution','1152x648','--disable-vsync')}else{@('--headless')}
    $options=@($video)+@('--path',$game,'--log-file',(Join-Path $dir 'engine.log'))
    if($script -ne 'timing.gd'){$options+=@('--fixed-fps','60')}
    $options+=@('--script',(Join-Path $PSScriptRoot $script),'--','--qa-still-frames','--day-one-test',"--qa-dir=res://$location")+$flags
    & $engine @options *> (Join-Path $dir 'console.log')
    if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath (Join-Path $dir 'engine.log') -Pattern '^(ERROR|SCRIPT ERROR|SHADER ERROR):' -Quiet)){throw "See $dir"}
}
Run-Case 'walk' 'verify.gd' @('--practice-passage') $true
Run-Case 'sections' 'section.gd' @()
Run-Case 'restore' 'reopen.gd' @("--from=res://$base/walk/bridge.cfg")
Run-Case 'teaching' '../indoor_delivery/verify_shift.gd' @()
Run-Case 'offer' 'reopen.gd' @("--from=res://$base/teaching/completed.cfg",'--counter')
Run-Case 'single' '../indoor_delivery/free_order.gd' @("--checkpoints=res://$base/teaching")
Run-Case 'lunch' '../lunch_run/verify.gd' @('--practice-lunch')
if($Timing){Run-Case 'timing' 'timing.gd' @('--practice-passage') $true}
