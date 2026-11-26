"""Make review sheets from native frames. Frames stay in their original camera order."""
from pathlib import Path
import json, sys
from PIL import Image, ImageDraw, ImageFont

def group(key):
    if key.startswith("core_"):return "core"
    if key.startswith("plot_"):return key.rsplit("_",1)[1]
    return "registered"

def publish(source, out, prefix, records, width=385):
    out.mkdir(parents=True,exist_ok=True)
    fontfile=Path(__file__).resolve().parents[2]/"assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf"
    font=ImageFont.truetype(str(fontfile),15)
    written={}
    for offset in range(0,len(records),12):
        chunk=records[offset:offset+12]
        h=width*9//16
        sheet=Image.new("RGB",(width*3,(h+30)*((len(chunk)+2)//3)),(242,238,231))
        draw=ImageDraw.Draw(sheet)
        name=f"{prefix}_{offset//12+1:02d}.jpg"
        for i,r in enumerate(chunk):
            key=r["key"]
            path=source/(key+".jpg")
            if not path.exists():path=source/(key+".png")
            with Image.open(path) as img:
                img=img.convert("RGB");img.thumbnail((width,h),Image.Resampling.LANCZOS)
                x=(i%3)*width;y=(i//3)*(h+30)
                sheet.paste(img,(x,y))
            text=key.removeprefix("core_")+"  "+str(r.get("title",""))
            draw.text((x+5,y+h+3),text,font=font,fill=(48,43,39))
            written[key]=name
        sheet.save(out/name,quality=89)
    return written

if __name__=="__main__":
    src,out=map(Path,sys.argv[1:3])
    rows=json.loads((src/"views.json").read_bytes())["views"]
    for k in dict.fromkeys(group(r["key"]) for r in rows):
        publish(src,out,k,[r for r in rows if group(r["key"])==k])
