"""Register Baidu panorama metadata against the unchanged project control."""
from hashlib import file_digest
from math import asin, atan2, copysign, cos, degrees, hypot, pi, sin, sqrt
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET

BAIDU_BANDS = (12890594.86, 8362377.87, 5591021., 3481989.83, 1678043.12, 0.)
# Piecewise Baidu Mercator inverse polynomial, in the provider's metre units.
MC_TO_LL = (
    (1.410526172116255e-8,8.98305509648872e-6,-1.9939833816331,200.9824383106796,-187.2403703815547,91.6087516669843,-23.38765649603339,2.57121317296198,-.03801003308653,17337981.2),
    (-7.435856389565537e-9,8.983055097726239e-6,-.78625201886289,96.32687599759846,-1.85204757529826,-59.36935905485877,47.40033549296737,-16.50741931063887,2.28786674699375,10260144.86),
    (-3.030883460898826e-8,8.98305509983578e-6,.30071316287616,59.74293618442277,7.357984074871,-25.38371002664745,13.45380521110908,-3.29883767235584,.31744743859339,6856817.37),
    (-1.981981304930552e-8,8.983055099779535e-6,.03278182852591,40.31678527705744,.65659298677277,-4.44255534477492,.85341911805263,.12923347998204,-.04625736007561,4482777.06),
    (3.09191371068437e-9,8.983055096812155e-6,.00006995724062,23.10934304144901,-.00023663490511,-.6321817810242,-.00663494467273,.03430082397953,-.00466043876332,2555164.4),
    (2.890871144776878e-9,8.983055095805407e-6,-.00000003068298,7.47137025468032,-.00000353937994,-.02145144861037,-.00001234426596,.00010322952773,-.00000323890364,826088.5),
)


def bd_mercator(x, y):
    a, b, *terms = next(coefs for band,coefs in zip(BAIDU_BANDS,MC_TO_LL) if abs(y) >= band)
    divisor = terms.pop()
    y_scaled = abs(y)/divisor
    return (copysign(a+b*abs(x),x),copysign(sum(v*y_scaled**j for j,v in enumerate(terms)),y))


def bd_to_gcj(lon, lat):
    x,y = lon-.0065,lat-.006
    k=pi*3000./180.
    r=hypot(x,y)-.00002*sin(y*k)
    angle=atan2(y,x)-.000003*cos(x*k)
    return r*cos(angle),r*sin(angle)


def from_wgs84(lon, lat):
    """Forward GCJ offset in Chongqing, used to invert by residual."""
    x,y=lon-105,lat-35
    common=(20*sin(6*x*pi)+20*sin(2*x*pi))*2./3.
    phi = common-100+2*x+3*y+.2*y*y+.1*x*y+.2*sqrt(abs(x))
    phi += (20*sin(y*pi)+40*sin(y*pi/3)+160*sin(y*pi/12)+320*sin(y*pi/30))*2./3.
    lam = common+300+x+2*y+.1*x*x+.1*x*y+.1*sqrt(abs(x))
    lam += (20*sin(x*pi)+40*sin(x*pi/3)+150*sin(x*pi/12)+300*sin(x*pi/30))*2./3.
    r=lat*pi/180.
    magic=1-.006693421622965943*sin(r)**2
    radius=6378245.
    return (lon+degrees(lam*sqrt(magic)/(radius*cos(r))),
            lat+degrees(phi*magic**1.5/(radius*(1-.006693421622965943))))


def to_wgs84(lon,lat):
    x,y=lon,lat
    for attempt in range(12):
        u,v=from_wgs84(x,y)
        error=max(abs(u-lon),abs(v-lat))
        if error<1.e-10:
            return (x,y),error
        x -= u-lon
        y -= v-lat
    raise ValueError(f"GCJ inversion residual {error}")


def project(point,transform):
    x=point[0]-transform["wgs_origin"][0]
    y=point[1]-transform["wgs_origin"][1]
    a,b,c=transform["matrix"]
    return [x*a[i]+y*b[i]+c[i] for i in range(2)]


def line_hit(point, line):
    e,n=point
    candidates=[]
    for a,b in zip(line,line[1:]):
        de,dn=b[0]-a[0],b[1]-a[1]
        length_sq=de*de+dn*dn
        if not length_sq:
            continue
        t=min(1.,max(0.,((e-a[0])*de+(n-a[1])*dn)/length_sq))
        x,y=a[0]+t*de,a[1]+t*dn
        candidates.append((hypot(e-x,n-y),[x,y]))
    return min(candidates)


def digest(path):
    with path.open("rb") as source:
        return file_digest(source,"sha256").hexdigest()


def report(field, calibration, osm, legacy):
    reference=json.loads(calibration.read_text())
    transform=reference["transform"]
    assert digest(osm)==reference["source_sha256"]
    xml=ET.parse(osm)
    nodes={n.attrib["id"]:project((float(n.attrib["lon"]),float(n.attrib["lat"])),transform)
           for n in xml.findall("node")}
    roads={}
    for way in xml.findall("way"):
        tags={tag.attrib["k"]:tag.attrib["v"] for tag in way.findall("tag")}
        if "highway" not in tags: continue
        refs=[node.attrib["ref"] for node in way.findall("nd")]
        if len(refs)>1 and all(n in nodes for n in refs):
            roads[int(way.attrib["id"])]=dict(name=tags.get("name"),tags=tags,line=[nodes[n] for n in refs],
                 version=way.attrib.get("version"))
    old={r["panorama"]:r for r in json.loads(legacy.read_text())["records"]}
    sites={r["plot"]:r for r in reference["plots"]}
    records=[]
    for row in json.loads((field/"manifest.json").read_text()):
        pid=row["pano"]
        path=field/f"{pid}.json"
        if not path.is_file():
            records.append(row)
            continue
        metadata=json.loads(path.read_bytes())["content"][0]
        x,y=metadata["X"],metadata["Y"]
        bd=bd_mercator(x/100.,y/100.)
        gcj=bd_to_gcj(*bd)
        wgs,error=to_wgs84(*gcj)
        en=project(wgs,transform)
        previous=old.get(pid)
        previous_en=previous["en"] if previous else [-64.1416+(x-1186388416)*.0087,-175.7522+(y-342521910)*.00832]
        center=sites[row["plot"]]["center_en"]
        e,n=center[0]-en[0],center[1]-en[1]
        nearest=sorted((line_hit(en,stats["line"])[0],way) for way,stats in roads.items())
        selected={way: distance for distance,way in nearest[:5]}
        if row["plot"] in (45,46):
            selected[1025797976]=line_hit(en,roads[1025797976]["line"])[0]
        tests=[]
        for way,dist in selected.items():
            props=roads[way]
            tests.append(dict(way=way,name=props["name"],version=props["version"],tags=props["tags"],
                corrected_m=dist,legacy_m=line_hit(previous_en,props["line"])[0],
                corrected_projection_en=line_hit(en,props["line"])[1]))
        records.append({**row,"date":metadata["Date"],"raw_mc_cm":[x,y],"source_height_metadata":metadata.get("Z"),
                        "bd09":bd,"gcj02":gcj,"wgs84":wgs,"gcj_roundtrip_max_degrees":error,"en":en,
                        "legacy_en":previous_en,"legacy_published_angle":previous.get("angle") if previous else None,
                        "legacy_reference":digest(legacy) if previous else None,
                        "delta_east_north_m":[a-b for a,b in zip(en,previous_en)],
                        "old_centre_range_m":hypot(e,n),"old_centre_bearing_deg":degrees(atan2(e,n))%360,
                        "road_controls":tests})
    return {"map_sha256":digest(osm),"project_control":reference["project_control"],"transform":transform,
            "attribution":reference["attribution"],"records":records}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("field","calibration","osm","legacy","output"):
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    result=report(args.field,args.calibration,args.osm,args.legacy)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
