param([ValidateSet('import','capture','defects','survey','lane','street','rider','character','gameplay','delivery','performance','district','movie')][string]$Phase='capture',
      [string]$Run='current',[string]$Profile='render_profile_r21')
$ErrorActionPreference='Stop'
if($Run -notmatch '^[a-zA-Z0-9_-]+$' -or $Profile -notmatch '^[a-zA-Z0-9_-]+$'){throw 'Invalid evidence or profile name'}
$p=Join-Path $PSScriptRoot 'project/chongqing_godot_v05'
$engine=Join-Path $PSScriptRoot 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$relative="verification_r21/$Run"
$d=Join-Path $p "$relative/logs"
New-Item -ItemType Directory -Force -Path $d | Out-Null
$art="--art-profile=res://assets/$Profile.json"
$qa="--qa-dir=res://$relative"
$views='street_entry,central_steps,r20_tree_court,r20_neighbor,noodle_corner,roofscape,narrow_passage,residential_entry,west_lane'
$arguments=switch($Phase){
 'import' {@('--headless','--editor','--import')}
 'capture' {@('--','--capture','--capture-size=1600x900','--settle-frames=45',"--capture-view=$views","--capture-dir=res://$relative/captures",$art)}
 'defects' {@('--','--capture','--capture-size=1600x900','--settle-frames=45','--capture-view=r16_scooter,r17_A04_entry,r16_roof,r16_meter,r17_worker_entry,r17_worker_door,r16_clothesline,r17_west_route',"--capture-dir=res://$relative/defect_views",$art)}
 'street' {@('--headless','--fixed-fps','60','--','--r19-street-test',$qa,$art)}
 'rider' {@('--headless','--fixed-fps','60','--','--r18-rider-test',"$qa/rider",$art)}
 'survey' {@('--headless','--fixed-fps','60','--','--survey-test',"--test-report=res://$relative/survey.json",$art)}
 'lane' {@('--headless','--fixed-fps','60','--','--r20-lane-test',$qa,$art)}
 'character' {@('--headless','--fixed-fps','60','--','--r18-shopkeeper-test',$qa,$art)}
 'gameplay' {@('--headless','--fixed-fps','60','--','--r16-test',$qa,$art)}
 'delivery' {@('--headless','--fixed-fps','60','--','--r17-delivery-test',$qa,$art)}
 'performance' {@('--','--r16-performance','--perf-views=street_entry,central_steps,r20_tree_court,roofscape,noodle_corner,narrow_passage',$qa,$art)}
 'district' {@('--headless','--fixed-fps','60','--script',(Join-Path $PSScriptRoot 'test_district_r21.gd'),'--',$art,$qa)}
 'movie' {@('--resolution','1280x720','--fixed-fps','30','--write-movie',(Join-Path $PSScriptRoot "scene_r21/district_$Run.avi"),'--script',(Join-Path $PSScriptRoot 'capture_district_walk.gd'),'--',$qa,$art)}
}
$log=Join-Path $d "$Phase.log"
& $engine --path $p --log-file $log @arguments *> (Join-Path $d "$Phase.console.txt")
if($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath $log -Pattern '^ERROR:|SCRIPT ERROR:|SHADER ERROR:|Parse Error:' -Quiet)){throw "$Phase failed. See $log"}
Write-Output "$Phase passed for $Run"
