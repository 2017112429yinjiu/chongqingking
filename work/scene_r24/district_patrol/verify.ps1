param([Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run,[switch]$Timing)
$ErrorActionPreference='Stop'
$game=(Resolve-Path "$PSScriptRoot/../../project/chongqing_godot_v05").Path
$prefix="verification_r24/district_patrol/$Run"
if(Test-Path -LiteralPath "$game/$prefix"){throw "Choose a fresh run name"}
function Case([string]$label,[string]$script,[string[]]$options,[bool]$draw=$false){
    & "$PSScriptRoot/run.ps1" -Run "$Run/$label" -Script $script -Extra $options -Draw:$draw
    if($LASTEXITCODE -or (Select-String -LiteralPath "$game/$prefix/$label/engine.log" -Pattern '^(SCRIPT ERROR|SHADER ERROR|ERROR):' -Quiet)){
        throw "Inspect $game/$prefix/$label"
    }
}
Case 'ride' 'patrol.gd' @() $true
Case 'turns' 'junctions.gd' @() $true
Case 'older_crossings' 'legacy_views.gd' @('--practice-passage') $true
Case 'pavement' 'pavement.gd' @()
Case 'sites' 'sites.gd' @('--practice-passage') $true
Case 'home' 'local_route.gd' @('--practice-passage') $true
Case 'bridge' '../vertical_run/verify.gd' @('--practice-passage') $true
Case 'sections' '../vertical_run/section.gd' @()
Case 'restore' '../vertical_run/reopen.gd' @("--from=res://$prefix/bridge/bridge.cfg")
Case 'teaching' '../indoor_delivery/verify_shift.gd' @()
Case 'counter' '../vertical_run/reopen.gd' @("--from=res://$prefix/teaching/completed.cfg",'--counter')
Case 'single' '../indoor_delivery/free_order.gd' @("--checkpoints=res://$prefix/teaching")
Case 'lunch' '../lunch_run/verify.gd' @('--practice-lunch')
foreach($label in 'ride','turns','older_crossings','sites','home','bridge'){
    & "$PSScriptRoot/sheet.ps1" "$game/$prefix/$label" "$game/$prefix/$label/visuals.jpg"
}
if($Timing){
    $dir=New-Item -ItemType Directory -Path "$game/$prefix/timing"
    $engine=(Resolve-Path "$PSScriptRoot/../../tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe").Path
    & $engine --resolution 1152x648 --disable-vsync --path $game --log-file "$dir/engine.log" --script "$PSScriptRoot/../vertical_run/timing.gd" -- --day-one-test --practice-passage "--qa-dir=res://$prefix/timing" *> "$dir/console.log"
    if($LASTEXITCODE){throw "Inspect $dir"}
}
