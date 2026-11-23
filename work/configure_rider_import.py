from pathlib import Path
root=Path(__file__).resolve().parent
for path in [root/'project/chongqing_godot_v05/assets/characters/rider_r18.glb.import',root/'characters/rider_r18_trial/godot/assets/rider.glb.import']:
    if not path.exists():continue
    text=path.read_text()
    text=text.replace('_subresources={}','_subresources={\n"nodes": {\n"PATH:AnimationPlayer": {\n"optimizer/enabled": false\n}\n}\n}')
    path.write_text(text)
    print(path.name,'contact animation optimizer disabled')
