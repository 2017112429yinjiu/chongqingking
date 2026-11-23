param(
    [ValidateSet('import','walk','walk_visual','street','delivery','survey','captures','native1080','smoke','traffic','traffic_views','corner','corner_visual','defect_views','cloth','cloth1080','cloth_final')][string]$Phase='walk',
    [string]$Project=(Join-Path $PSScriptRoot 'project/chongqing_godot_v05'),
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Run='build17b',
    [string[]]$ArtArgs=@(),
    [switch]$Baseline
)
$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$projectPath=(Resolve-Path -LiteralPath $Project).Path
$folder="res://verification_r24/$Run"
$base=Join-Path $projectPath "verification_r24/$Run"
New-Item $base -ItemType Directory -Force | Out-Null
$qa="--qa-dir=$folder"
$views='r23_main_road,r24_stall,r24_counter,r24_repair,r24_stairs,r24_court,r23_street_support,r24_viaduct,r24_junction,r24_verge'
$extra=switch($Phase) {
 'import' {@('--headless','--editor','--import')}
 'walk' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'walk_frontage_r24.gd'),'--',$qa)}
 'walk_visual' {@('--position','2600,120','--resolution','1280x720','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'walk_frontage_r24.gd'),'--',$qa)}
 'traffic' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'traffic_support_r24.gd'),'--',$qa,'--traffic-motion')}
 'traffic_views' {@('--position','2600,120','--resolution','1280x720','--script',(Join-Path $PSScriptRoot 'compare_traffic_r24.gd'),'--',$qa)}
 'corner' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'walk_junction_r24.gd'),'--',$qa)}
 'corner_visual' {@('--position','2600,120','--resolution','1280x720','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'walk_junction_r24.gd'),'--',$qa)}
 'street' {@('--headless','--fixed-fps','60','--','--r23-test',$qa)}
 'delivery' {@('--headless','--fixed-fps','60','--','--r17-delivery-test',$qa)}
 'survey' {@('--headless','--fixed-fps','60','--','--survey-test',"--test-report=$folder/survey.json")}
 'smoke' {@('--headless','--','--smoke-test',"--test-report=$folder/smoke.json")}
 'cloth' {@('--position','2600,120','--resolution','1280x720','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'inspect_washcloth_r24.gd'),'--',$qa)}
 'defect_views' {@('--position','2600,120','--','--capture','--capture-size=1600x900','--settle-frames=35','--capture-view=r23_laundry,r23_brick,r23_court_bench,r23_street_support,r23_garden,r23_shop_window,r23_shutter', "--capture-dir=$folder/defect_views")}
 'captures' {@('--position','2600,120','--','--capture','--capture-size=1600x900','--settle-frames=35',"--capture-view=$views","--capture-dir=$folder/captures")}
 'cloth_final' {@('--position','2600,120','--resolution','1280x720','--disable-vsync','--script',(Join-Path $PSScriptRoot 'inspect_washcloth_r24.gd'),'--',$qa,'--cloth-perf')}
 'cloth1080' {@('--position','2600,120','--disable-vsync','--script',(Join-Path $PSScriptRoot 'performance_1080_r23.gd'),'--',$qa,'--perf-views=r23_laundry,r23_court_bench')}
 'native1080' {@('--position','2600,120','--disable-vsync','--script',(Join-Path $PSScriptRoot 'performance_1080_r23.gd'),'--',$qa,'--perf-views=r23_main_road,r24_counter,r24_court,r24_viaduct,r24_verge')}
}
if($Baseline -and $Phase -ne 'import') {$extra+='--art-profile=res://assets/render_profile_r23.json'}
& $engine --path $projectPath --log-file (Join-Path $base "$Phase.log") @extra @ArtArgs
exit $LASTEXITCODE

