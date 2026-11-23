param(
  [ValidateSet('import','launch','capture','river','performance','native1080','aa1080','art','survey','delivery','lane','gameplay','district','street','defects','rider','movie')][string]$Phase='capture',
  [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Run='import01',
  [switch]$Baseline
)
$ErrorActionPreference='Stop'
$project=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$relative="verification_r22/$Run"
$logs=Join-Path $project "$relative/logs"
New-Item $logs -ItemType Directory -Force|Out-Null
$art=if($Baseline){'--art-profile=res://verification_r22/base_profile.json'}else{'--art-profile=res://assets/render_profile_r22.json'}
$qa="--qa-dir=res://$relative"
$fixed='roofscape,noodle_corner,central_steps,street_entry,r20_tree_court,residential_entry,west_lane,r22_breakfast,r22_roof_garden,r22_roof_wash,r22_river_street,r22_river_overview,r22_river_detail'
$arguments=switch($Phase){
 'import' {@('--headless','--editor','--import')}
 'launch' {@('--quit-after','125')}
 'movie' {@('--resolution','1280x720','--fixed-fps','30','--write-movie',(Join-Path $PSScriptRoot "scene_r22/district_$Run.avi"),'--script',(Join-Path $PSScriptRoot 'capture_river_walk_r22.gd'),'--',$qa,$art)}
 'capture' {@('--','--capture','--capture-size=1600x900','--settle-frames=45',"--capture-view=$fixed","--capture-dir=res://$relative/captures",$art)}
 'river' {@('--','--capture','--capture-size=1600x900','--settle-frames=45','--capture-view=r22_river_street,r22_river_overview,r22_river_detail',"--capture-dir=res://$relative/river",$art)}
 'defects' {@('--','--capture','--capture-size=1600x900','--settle-frames=45','--capture-view=r16_scooter,r17_A04_entry,r16_roof,r16_meter,r17_worker_entry,r17_worker_door,r16_clothesline,r17_west_route',"--capture-dir=res://$relative/defect_views",$art)}
 'performance' {@('--','--r16-performance','--viewport-gpu','--perf-views=street_entry,central_steps,r20_tree_court,roofscape,noodle_corner,narrow_passage,r22_breakfast,r22_river_street,r22_river_overview',$qa,$art)}
 'native1080' {@('--script',(Join-Path $PSScriptRoot 'performance_1080_r22.gd'),'--',$qa,$art)}
 'aa1080' {@('--script',(Join-Path $PSScriptRoot 'performance_1080_r22.gd'),'--','--post-aa-trial',$qa,$art)}
 'art' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'test_roofs_r22.gd'),'--',$art,$qa)}
 'survey' {@('--headless','--fixed-fps','60','--','--survey-test',"--test-report=res://$relative/survey.json",$art)}
 'delivery' {@('--headless','--fixed-fps','60','--','--r17-delivery-test',$qa,$art)}
 'lane' {@('--headless','--fixed-fps','60','--','--r20-lane-test',$qa,$art)}
 'gameplay' {@('--headless','--fixed-fps','60','--','--r16-test',$qa,$art)}
 'rider' {@('--headless','--fixed-fps','60','--','--r18-rider-test',"$qa/rider",$art)}
 'district' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'test_district_r21.gd'),'--',$art,$qa)}
 'street' {@('--headless','--fixed-fps','60','--','--r19-street-test',$qa,$art)}
}
$log=Join-Path $logs "$Phase.log"
& $engine --path $project --log-file $log @arguments *> (Join-Path $logs "$Phase.console.txt")
if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:|Parse Error:' -Quiet)){throw "$Phase failed; see $log"}
Write-Output "$Phase passed for $Run"
