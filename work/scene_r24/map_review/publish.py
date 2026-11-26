"""Publish a completed survey. Input folders follow the names in README.md."""
from collections import Counter
from pathlib import Path
from atlas import publish as make_sheets, group as frame_group
import argparse
import hashlib
import json
import math
import zipfile
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[1] / "project/chongqing_godot_v05"
ASSETS = GAME / "assets/district_500"
ROOMS = {"bedroom": "卧室", "sitting_room": "起居室", "washroom": "洗漱间", "kitchen": "厨房"}

def read(path):
    return json.loads(path.read_bytes())

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def contains(x, y, ring):
    inside = False
    for (a, b), (c, d) in zip(ring, ring[1:] + ring[:1]):
        if (b > y) != (d > y) and x < (c - a) * (y - b) / (d - b) + a:
            inside = not inside
    return inside

def material_counts(path):
    data = read(path)
    rows = [r for r in data["nodes"] if r[1]]
    surfaces = [i for row in rows for i in row[8]]
    materials = set(surfaces) - {-1}
    return dict(geometry=len(data["nodes"]), visible=len(rows), visible_surfaces=len(surfaces),
                null_surfaces=surfaces.count(-1), material_count=len(materials),
                no_bound_texture=sum(not data["materials"][str(i)]["textures"] for i in materials),
                source_scenes=sorted({r[4] for r in rows}))

def lane_finishes(lanes):
    # Source weights at the centreline only. Separate paving meshes can cover the shader.
    with Image.open(ASSETS / "surface_mask.png") as image:
        mask = image.convert("RGB")
    weights = {}
    for lane in lanes:
        tally = weights.setdefault(lane["type"], Counter())
        for (ax, ay), (bx, by) in zip(lane["points"], lane["points"][1:]):
            length = math.hypot(bx - ax, by - ay)
            steps = max(1, math.ceil(length / .5))
            for i in range(steps):
                t = (i + .5) / steps
                x = (ax + (bx - ax) * t + 250) / 500
                y = (250 - ay - (by - ay) * t) / 500
                r, g, _ = mask.getpixel((min(mask.width-1,max(0,int(x*mask.width))),
                                         min(mask.height-1,max(0,int(y*mask.height)))))
                r, g = r/255, g/255
                cells = {"road":r, "paving":(1-r)*g, "bank_or_soil":(1-r)*(1-g)}
                tally[max(cells, key=cells.get)] += length / steps
    return {kind: {k:round(v,2) for k,v in tally.items()} for kind,tally in weights.items()}

def draw_map(path, layout, geo, rings, probes):
    size, margin, span = 980, 42, 876
    im = Image.new("RGB", (size, size+65), "#faf7f0")
    # Draw everything inside a clipped tile, including mapped roads reaching out of bounds.
    tile = Image.new("RGB", (span+1,span+1), "#e9e1cf")
    draw = ImageDraw.Draw(tile)
    fontfile = HERE.parents[1] / "assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf"
    font = lambda s:ImageFont.truetype(str(fontfile),s)
    def xy(v):return ((v[0]+250)*span/500,(250-v[1])*span/500)
    for role, color in [("outer","#bdd8dd"),("inner","#e9e1cf")]:
        for ring in rings:
            if ring["role"]==role:draw.polygon([xy(p) for p in ring["points"]],fill=color)
    for rows, color, width in [(geo["paths"],"#b8a98d",2),(geo["roads"],"#a3998e",4),(layout["lanes"],"#fffaf0",3)]:
        for row in rows:
            if len(row["points"])>1:draw.line([xy(p) for p in row["points"]], fill=color, width=width)
    for group in ["buildings","context_buildings"]:
        for row in geo[group]:
            if len(row["points"])>2:draw.polygon([xy(p) for p in row["points"]],outline="#c2ac8c")
    draw.rectangle((xy((-100,100)),xy((100,-100))),outline="#696b69",width=2)
    for plot in layout["plots"]:
        x,y=xy(plot["east_north"]); i=plot["plot_id"]
        color = "#195a80" if i==37 else "#327944" if i==42 else "#514c44"
        draw.ellipse((x-3,y-3,x+3,y+3),fill=color)
        draw.text((x+3,y-11),str(i),font=font(12),fill=color,stroke_width=1,stroke_fill="#f6f2e8")
    for key, val in probes.items():
        x,y=xy(val["xy"]); draw.ellipse((x-7,y-7,x+7,y+7),outline="#a8331f",width=3)
    im.paste(tile,(margin,64))
    draw=ImageDraw.Draw(im)
    draw.text((margin,10),"500 米巡检位置图",font=font(30),fill="#292b26")
    draw.text((size-265,25),"北 ↑    东 →    每边 500 m",font=font(16),fill="#46544b")
    draw.text((margin,949),"红圈  地形侵入室内（6 处）     蓝  37 号正门受阻     绿  42 号植被穿窗     数字  试作地块 ID",font=font(17),fill="#302f2c")
    draw.text((margin,985),"中央方框为原 200 米范围。道路和建筑轮廓据项目地图底稿。 © OpenStreetMap contributors · ODbL",font=font(16),fill="#505550")
    im.save(path,quality=90)

def poster(path, survey):
    picks = [("terrain_views/floor_w704006741_1.jpg","西北单层房 · 室内最高测点 1.139 m"),
             ("pixels/plot_56_room_live.jpg","56 号 · 地形盖住室内地砖"),
             ("pixels/plot_42_room_live.jpg","42 号 · 窗内树叶命中 036 号植株"),
             ("play/plot_40_upper.jpg","40 号院楼 · 红格床与柜钟"),
             ("play/plot_72_upper.jpg","72 号院楼 · 同组陈设再次出现"),
             ("school/story_walk/look_back.png","故事馆对照 · 从楼梯脚回望教室")]
    im=Image.new("RGB",(1200,520),"#f6f3ed")
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(HERE.parents[1]/"assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf"),16)
    for i,(p,title) in enumerate(picks):
        x,y=i%3*400,i//3*260
        with Image.open(survey/p) as frame:
            frame.thumbnail((400,225),Image.Resampling.LANCZOS);im.paste(frame,(x,y))
        draw.text((x+6,y+228),title,font=font,fill="#332f2b")
    im.save(path,quality=90)

def plot_index(base, plots, floors, direct, retests, through):
    rows=["# 71 个试作地块逐项记录","",
          "ID 取自布局的 plot_id。每栋均有街面和穿堂原图，68 栋另有普通住室原图。楼上院房另外计数。图像包内搜索例如 `play/plot_56_room.jpg`。室内走通与街面进门分别记录。", "",
          "| ID | 东 / 北（米） | 穿堂 | 普通房间（进出） | 楼上院房 | 街线直入 / 直出 | 复测及观察 |",
          "|---:|---|---|---|---|---|---|"]
    checks={r["name"]:r["pass"] for r in through}
    results={r["name"]:r["pass"] for r in direct}
    for index, plot in enumerate(plots):
        i=plot["plot_id"]; key=f"plot_{i:02}"; room=plot.get("room",{}).get("use")
        hall=checks[f"hall_{index:02}_out"]
        home="—" if not room else ROOMS[room]+(" ✓" if all(checks[f"household_{index:02}_{d}"] for d in ("out","back")) else " 受阻")
        flags=["通过" if results[f"street_{i:02}_{d}"] else "受阻" for d in ("in","out")]
        extra=[]
        subset=[r for r in retests if r["name"].startswith(f"stair_{i:02}_")]
        if subset:extra.append(f"复测 {sum(r['pass'] for r in subset)}/{len(subset)}")
        if i==0:extra.append("登记街口→修车→内院→街口通过；修车用途为玩法")
        if i in (1,2):extra.append("右侧斜切碰柱；经平台左右均可进出")
        if i==33:extra.append("楼梯三线双向通过")
        if i==37:extra.append("楼梯三线进门均撞挡墙")
        if i in (38,40,41,44):extra.append("侧梯双向通过")
        f=floors[key]
        if f["inner_above_15mm"]:extra.append(f"室内穿地 {f['inner_peak_m']:.3f} m")
        elif f["above_15mm"]:extra.append("近边缘 0.016 m")
        if f["plant_vertices_inside"]: extra.append("窗内植株已定位" if i==42 else "植被顶点入屋，需近看")
        x,y=plot["east_north"]
        rows.append(f"| {i} | {x:.1f} / {y:.1f} | {'通过' if hall else '受阻'} | {home} | {'重复红格床' if 'court' in plot else '—'} | {' / '.join(flags)} | {'；'.join(extra) or '见原图'} |")
    rows.extend(["","0 号已按同地段资料重做，柜台和院内布置含玩法推定。其余 70 个试作地块缺逐栋同址外观佐证。穿堂、房间及街线列的「通过」仅描述所测方向。四栋西北地图房与仁爱堂、小学另见[总报告](README.md)。",""])
    (base/"PLOTS.md").write_text("\n".join(rows),encoding="utf-8")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("survey","patrol","repair","output"):
        parser.add_argument("--"+name,type=Path,required=True)
    args=parser.parse_args()
    d, out=args.survey,args.output
    out.mkdir(parents=True,exist_ok=True)
    ev=out/"evidence";ev.mkdir(exist_ok=True)
    layout=read(ASSETS/"layout.json")
    geo=read(GAME/"source_data/geo_layout.json")
    water=read(GAME/"source_data/river_r22/river_plan.json")["rings"]
    misses=[(x,y) for x,y,hit,z in read(d/"play/ground.json") if not hit]
    wet=sum(any(contains(x,y,r["points"]) for r in water if r["role"]=="outer") and
            not any(contains(x,y,r["points"]) for r in water if r["role"]=="inner") for x,y in misses)
    direct=read(d/"approaches/approaches.json"); retests=read(d/"width_recheck/stairs.json")
    floors={r["key"]:r for r in read(d/"inner_floors/floors.json")};probes=read(d/"terrain_views/probes.json")
    stats={"play":material_counts(d/"play/nodes.json"),"art":material_counts(d/"art_views/nodes.json"),
           "frames":{p:len(read(d/p/"views.json")["views"]) for p in ("play","art_views","terrain_views","road_views_full")},
           "rooms":dict(Counter(p["room"]["use"] for p in layout["plots"] if "room" in p)),
           "water_grid":{"misses":len(misses),"in_registered_water":wet},
           "dominant_surface_metres_along_lane_centres":lane_finishes(layout["lanes"]),
           "paired_floor_points":sum(r["samples"] for r in floors.values()),
           "unpaired_floor_points":sum(r["unpaired"] for r in floors.values()),"intrusions":probes,
           "failed_direct":[r["name"] for r in direct if not r["pass"]],
           "failed_stairs":[r["name"] for r in retests if not r["pass"]]}
    digest = {}
    scenes = set(stats["play"]["source_scenes"] + stats["art"]["source_scenes"])
    for uri in sorted(scenes):
        with (GAME/uri.removeprefix("res://")).open("rb") as asset:
            digest[uri] = hashlib.file_digest(asset,"sha256").hexdigest()
    stats["visible_scene_file_sha256"] = digest
    for folder,grouping in [("play",frame_group),("terrain_views",lambda k:k.split("_")[0]),("road_views_full",lambda k:"roadview")]:
        records = read(d/folder/"views.json")["views"]
        for kind in dict.fromkeys(grouping(r["key"]) for r in records):
            make_sheets(d/folder,d/"sheets",kind,[r for r in records if grouping(r["key"])==kind])
    for src, group_name in [(d/"school/views","courts"),(d/"school/story_walk","school"),(args.repair/"views","repair")]:
        make_sheets(src,d/"sheets",group_name,[{"key":p.stem} for p in sorted(src.glob("*.png"))])
    save(ev/"summary.json",stats)
    plot_index(out,layout["plots"],floors,direct,retests,read(d/"all_halls/checks.json"))
    draw_map(ev/"map.jpg",layout,geo,water,probes)
    poster(ev/"findings.jpg",d)
    # Archive game observations only. The original photographic references have independent licences.
    def include(z, root, prefix, suffixes):
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix.lower() in suffixes:
                ext=p.suffix.lower()
                z.write(p, str(Path(prefix)/p.relative_to(root)), compress_type=zipfile.ZIP_DEFLATED if ext==".json" else zipfile.ZIP_STORED)
    with zipfile.ZipFile(ev/"native.zip","w",allowZip64=True) as z:
        for sub in ["play","art_views","terrain_views","pixels","inner_floors","approaches","width_recheck","all_halls","shared","homes","front_stairs","outer_roads","school","sheets","road_views_full"]:
            include(z,d/sub,sub,{".jpg",".png",".json"})
        z.write(d/"feet_full.json","feet_full.json",compress_type=zipfile.ZIP_DEFLATED)
        include(z,args.repair,"repair",{".json",".png",".jpg"})
        include(z,args.patrol,"patrol",{".json"})
    print(json.dumps({k:v for k,v in stats.items() if k not in ("play","art","intrusions")},ensure_ascii=False))

if __name__=="__main__":
    main()
