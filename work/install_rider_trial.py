"""Install the reviewed prototype into the development project, never package it."""
from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parent;project=root/'project/chongqing_godot_v05';source=root/'characters/rider_r18_trial'
backup=root/'checkpoints/R18_vehicle_pre01';backup.mkdir(parents=True,exist_ok=True)
for name in ['scripts/gameplay.gd','scripts/scooter_controller.gd','Docs/VEHICLE_SYSTEM.md','verification_r18/review_summary.json']:
    src=project/name;dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(src,dst)
for src,dest in [('rider.glb','characters/rider_r18.glb'),('scooter.glb','vehicles/scooter_r18.glb')]:
    target=project/'assets'/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/'godot/assets'/src,target)
shutil.copy2(root/'assets_incoming/rocketbox_research/LICENSE.md',project/'assets/characters/ROCKETBOX_MIT_LICENSE.txt')
report=json.loads((source/'build_report.json').read_text());report['status']='Integrated development candidate; not cinematic acceptance'
report['source_commit']=(root/'assets_incoming/rocketbox_research/COMMIT.txt').read_text().strip()
report['source_provenance']=str(root/'assets_incoming/rocketbox_research/PROVENANCE.json')
report['changes']=['Original seated and steering poses with measured hand/foot contacts','Reduced facial blendshapes to ARKit blink/smile/cheek set','Original helmet and straps','Retained Rocketbox facial/body textures; relinked paths and normalized metres','Original project scooter split into wheel/steering/stand nodes, softened panel edges and original vertex wear']
(project/'assets/characters/rider_r18_provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
credits=project/'assets/CREDITS.txt';text=credits.read_text(encoding='utf-8')
if 'Microsoft Rocketbox' not in text:
    text+='\nMicrosoft Rocketbox — Male_Adult_10 facial base and textures, MIT.\nCopyright (c) 2020 Microsoft\nSource: https://github.com/microsoft/Microsoft-Rocketbox\nRequired copyright and full permission notice: assets/characters/ROCKETBOX_MIT_LICENSE.txt\nModified for the rider: metre scale, material conversion, selected facial morphs, original contact animation and helmet. No Rocketbox motion library was imported.\n'
    credits.write_text(text,encoding='utf-8')
print('Development assets installed; originals and shopkeeper20 retained.')
