param(
    [ValidateSet('import','street','delivery','survey','captures','player','performance','native1080','editor')][string]$Phase='street',
    [string]$Project=(Join-Path $PSScriptRoot 'project/chongqing_godot_v05')
)
$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$projectPath=(Resolve-Path -LiteralPath $Project).Path
$base=Join-Path $projectPath 'verification_r23/current'
New-Item -Path $base -ItemType Directory -Force | Out-Null
$spec='--qa-dir=res://verification_r23/current'
$views='r23_main_road,r23_shutter,r23_court_bench,r23_laundry,r23_shop_window,r23_garden,r23_street_support,r23_brick'
if ($Phase -eq 'editor') {
    $gui=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64.exe'
    Start-Process -FilePath $gui -WorkingDirectory $projectPath -ArgumentList '--editor','--path','.','res://main.tscn'
    return
}
$extra=switch($Phase){
    'import' {@('--headless','--editor','--import')}
    'street' {@('--headless','--fixed-fps','60','--','--r23-test')}
    'delivery' {@('--headless','--fixed-fps','60','--','--r17-delivery-test',$spec)}
    'survey' {@('--headless','--fixed-fps','60','--','--survey-test','--test-report=res://verification_r23/current/survey.json')}
    'captures' {@('--position','2600,120','--','--capture','--capture-size=1600x900','--settle-frames=35',"--capture-view=$views",'--capture-dir=res://verification_r23/current/captures')}
    'player' {@('--position','2600,120','--resolution','1280x720','--script',(Join-Path $PSScriptRoot 'review_player_r23.gd'))}
    'native1080' {@('--position','2600,120','--disable-vsync','--script',(Join-Path $PSScriptRoot 'performance_1080_r23.gd'),'--',$spec)}
    'performance' {@('--position','2600,120','--resolution','1280x720','--disable-vsync','--','--r16-performance','--viewport-gpu','--perf-views=r23_main_road,r23_shop_window,r23_street_support',$spec)}
}
& $engine --path $projectPath --log-file (Join-Path $base "$Phase.log") @extra
exit $LASTEXITCODE

