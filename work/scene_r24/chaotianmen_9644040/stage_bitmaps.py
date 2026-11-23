from pathlib import Path
from PIL import Image, ImageOps
import json
root=Path(__file__).resolve().parent
stage=root/"review_textures"
stage.mkdir(exist_ok=True)
index={}
for src in (root/"source").iterdir():
    if src.suffix.lower() not in {".jpg",".jpeg",".png",".bmp",".dds",".tga",".tif",".tiff",".gif",".psd"}: continue
    try:
        with Image.open(src) as im:
            im.thumbnail((1024,1024))
            dst=stage/(src.name+".jpg")
            im.convert("RGB").save(dst,quality=88)
        index[src.name.casefold()]=dst.name
    except (OSError,ValueError) as exc:print(src.name,str(exc)[:90])
(stage/"index.json").write_text(json.dumps(index),encoding="utf8")
print(len(index))

