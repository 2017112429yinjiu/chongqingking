param([ValidateSet('rooms','contacts','life','turns','seams','paving','market','delivery','smoke','street','views','before','walk','window720','window1080','prior720','prior1080')][string]$Phase='rooms',
 [string]$Run='build15', [string]$StudyDir=$PSScriptRoot, [string]$Profile=(Join-Path $PSScriptRoot 'candidate.json'),
 [string]$Views='r24_main_tea_window,r24_main_supper_window,r24_west_pantry,r23_main_road,r24_west_kitchen')
$ErrorActionPreference='Stop'
$work=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$project=Join-Path $work 'project/chongqing_godot_v05'
$engine=Join-Path $work 'tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$qa="res://verification_r24/$Run"
$art=@()
$default=Join-Path $project 'assets/render_profile_r24.json'
if ((Get-FileHash $default).Hash -ne (Get-FileHash $Profile).Hash){$art+="--art-profile=$Profile"}
$prior=Join-Path $work 'scene_r24/courtyard_life'
switch ($Phase) {
  {$_ -in @('rooms','contacts','life','turns','seams','paving')} {
    $script=switch ($Phase) {
      'rooms' { Join-Path $PSScriptRoot 'audit.gd' }
      'contacts' { Join-Path $work 'scene_r24/stair_neighborhood/audit.gd' }
      'life' { Join-Path $prior 'audit.gd' }
      'turns' { Join-Path $prior 'turns.gd' }
      'seams' { Join-Path $work 'scene_r24/city_frame_11864101/walk_seams.gd' }
      'paving' { Join-Path $prior 'paving/test.gd' }
    }
    $source=if($Phase -eq 'paving'){Join-Path $prior 'paving'}else{$prior}
    & $engine --path $project --headless --fixed-fps 60 --script $script -- @art "--qa-dir=$qa" $source
  }
  {$_ -in @('views','before')} {
    $dir=if($Phase -eq 'views'){'current'}else{'before'}
    $args2=@('--','--capture','--capture-size=1280x720','--settle-frames=20',"--capture-view=$views","--capture-dir=$StudyDir/$dir")
    if($Phase -eq 'before'){$args2+="--art-profile=$PSScriptRoot/before.json"}else{$args2+=$art}
    & $engine --path $project --position 2600,120 @args2
  }
  'walk' { & $engine --path $project --position 2600,110 --resolution 960x540 --fixed-fps 60 --script (Join-Path $PSScriptRoot 'walk.gd') -- @art "$StudyDir/walk_current" }
  {$_ -in @('window720','window1080','prior720','prior1080')} {
    $resolution=if($Phase.EndsWith('720')){'1280x720'}else{'1920x1080'}
    $opts=@('--','--timing')
    if($Phase.StartsWith('prior')){$opts+="--art-profile=$PSScriptRoot/before.json"}else{$opts+=$art}
    $opts+=Join-Path $project ("verification_r24/$Run/"+$Phase)
    & $engine --path $project --position 40,45 --resolution $resolution --disable-vsync --script (Join-Path $PSScriptRoot 'walk.gd') @opts
  }
  default {
    $cmd=if($Phase -eq 'market'){'walk'}else{$Phase}
    & (Join-Path $work 'verify_frontage_r24.ps1') -Phase $cmd -Run $Run -ArtArgs $art
  }
}
exit $LASTEXITCODE
