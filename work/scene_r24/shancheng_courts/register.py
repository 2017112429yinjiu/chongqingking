"""Register the published site plan near the delivery fork to the existing Shancheng map."""
from pathlib import Path
import json
import numpy as np

here = Path(__file__).resolve().parent
project = here.parents[2] / "work/project/chongqing_godot_v05"
geo = json.loads((project / "source_data/geo_layout.json").read_bytes())
trace = np.array(next(p["points"] for p in geo["paths"] if p["id"] == 734116601))
# Figure 8, 1080 x 736 px. Points below refer to the original, uncropped image.
# The SE junction is more legible on the resource map (Fig 3) and oblique views.
pivot = np.array([509.0, 425.8])
along_map = np.array([195., 273.])
along_map /= np.linalg.norm(along_map)
along_game = trace[36] - trace[35]
along_game /= np.linalg.norm(along_game)
across_map = np.array([-along_map[1], along_map[0]])
across_game = np.array([along_game[1], -along_game[0]])
metres_per_pixel = 50 / 110
def point(pixel):
    v = np.asarray(pixel) - pivot
    return (trace[37] + metres_per_pixel * ((v @ along_map)*along_game + (v @ across_map)*across_game)).round(4).tolist()

# Each ordered ring starts with the facade facing its public entrance.
# Nave ends exactly at the transverse wing, with no double room at the junction.
wings = {
    "renai_long": [[431.8,323.2],[506.2,428.4],[488.6,441.2],[414.2,340.4]],
    "renai_cross": [[433,322],[391.8,362.4],[369,339.6],[410.2,299.2]],
    "jinma_classrooms": [[469.8,290.4],[535,320.8],[549.8,292],[484.6,261.2]]
}

references = [
    {"id":"plan","publisher":"众绘山城；图3与图8转载于《“天上街市”，人间烟火：重庆山城巷更新实践》","url":"https://bbs.co188.com/thread-10503600-1-1.html","use":"Named buildings, relative plan and scale. Only measurements and site identification transcribed."},
    {"id":"renai_photo","publisher":"渝中区人民政府；既象实景","url":"https://www.cqyz.gov.cn/zjyz/lyyz/lswh/tk/202504/t20250421_14541659.html","use":"Long wing, return wing, slate roof, red eaves trim, segmented arches, recessed rectangular attic lights and round tracery at the end bay."},
    {"id":"school_photo","publisher":"渝中发布，金马寺小学实景，图13","url":"https://bbs.co188.com/thread-10503600-1-1.html","use":"Two levels, paired outward opening timber casements and transoms, center through-opening, low eaves, smooth pale masonry and tree-shaded flagstone court."},
    {"id":"library","publisher":"重庆日报，山城·时光里图书馆采访及馆内实景","url":"https://app.cqrb.cn/html/2022-07-21/1253645_pc.html","use":"Brick piers, display tables, timber cases, donated books and the tree-shaded front court."},
    {"id":"levels","publisher":"华龙网，书店主理人采访","url":"https://www.cqnews.net/1/detail/1270122359964934144/web/content_1270122359964934144.html","use":"The library is upstairs; the ground floor is the story gallery. Exact stair alignment is not surveyed."},
    {"id":"garden","publisher":"道合设计，吉盛生态品牌管理中心摄影","url":"https://mooool.com/wilderness-garden-theater-by-donehome.html","use":"Adjacency of the public walk, planted garden and ruins. Garden boundary has not been surveyed."},
    {"id":"map","publisher":"© OpenStreetMap contributors; ODbL 1.0","url":"https://www.openstreetmap.org/way/734116601","use":"Project coordinates, centerline controls and shared footway junction; the separate outline 585541371 labels the complex and is not the long wing."},
    {"id":"overhead","publisher":"Esri World Imagery and its imagery providers","url":"https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9","use":"Independent visual check of roof directions, the roadway/bridge and the planted garden. No raster included in the game or public repository."}
]
data = {"registered_plan":"Figure 8. Local fit at way 734116601 vertex 37, bearing from 35 to 36. Scale 50 m / 110 px. Roof diagram is generalized. Positions, heights and interior dimensions are approximate.",
        "anchor_pixel":pivot.tolist(),"anchor_east_north":trace[37].tolist(),"references":references,
        "buildings":[{"id":key,"plan_pixels":ring,"points":[point(q) for q in ring],"photo":"school_photo" if key.startswith("jinma") else "renai_photo"} for key,ring in wings.items()],
        "retired":{"3":"elevated crossing / road at pickup approach","5":"elevated crossing / roadside at pickup approach","47":"planted slope at Renai garden","48":"garden paths and trees west of the delivery court"},
        "preserved":"0 is an active repair shop on the garden edge; 4 is attached to a core rail repair. Their in-game identities remain in the migration queue."}
(here / "registered.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n", encoding="utf-8")
