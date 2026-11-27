"""Freeze the same six cameras for the historical and current game."""
import argparse
import json
from math import cos, hypot, sin
from pathlib import Path


def load(path):
    return json.loads(path.read_bytes())


def local_point(plot, u, v, rise):
    c, s = cos(plot["bearing"]), sin(plot["bearing"])
    e, n = plot["east_north"]
    return [e+c*u-s*v,n+s*u+c*v,plot["height"]+rise]


def outline(plot):
    w, d = plot["width"]/2., plot["depth"]/2.
    return [local_point(plot,u,v,0.)[:2] for u,v in ((-w,-d),(w,-d),(w,d),(-w,d))]


def separation(point, ring):
    e,n = point[:2]
    distances, orientation = [], []
    for (x0,y0),(x1,y1) in zip(ring,ring[1:]+ring[:1]):
        x,y = x1-x0,y1-y0
        t = min(1.,max(0.,((e-x0)*x+(n-y0)*y)/(x*x+y*y)))
        distances.append(hypot(e-x0-t*x,n-y0-t*y))
        orientation.append(x*(n-y0)-y*(e-x0))
    return {"fold_enu":point,"old_outline_en":ring,"horizontal_distance_to_edge_m":min(distances),
            "inside_old_outline":min(orientation)>=0. or max(orientation)<=0.}


def raised(row,height):
    return [row[0],row[1],row[2]+height]


def shot(name, eye, aim, fov=64.):
    return {"file":name+".png","eye_enu":eye,"target_enu":aim,"fov_deg":fov}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ("layout","market","layers","out"):
        parser.add_argument(arg,type=Path)
    args=parser.parse_args()
    plots={p["plot_id"]:p for p in load(args.layout)["plots"]}
    market=load(args.market)
    levels=load(args.layers)
    low=levels["low_outside_footprint"]
    up=levels["adjacent_upper_walkway"]
    context=levels["registered_low_road_context"]
    context_ground=next(
        ([*sample["east_north"],hit[1]] for sample in context[1:]+context[:1]
         for hit in sample["layers"] if hit[0].startswith(("COL_Outer500_Surface_","COL_R24_")) and hit[2]>.75),
        None,
    )
    approach=low["start_enu"] if context_ground is None else context_ground
    market_gate=local_point(plots[1],plots[1]["door_u"],-plots[1]["depth"]/2.+.50,1.32)
    upper_station=levels["upper_columns"][3]["enu"]
    upper_return=levels["upper_columns"][1]["enu"]
    shots=[
        shot("01-street-approach",raised(market["start_enu"],1.61),market_gate),
        shot("01-hall-look-back",raised(market["turn_enu"],1.60),market_gate),
        shot("52-low-street-approach",raised(approach,1.61),[-176.5,-100.2,12.0],62.),
        shot("52-low-exterior-look-back",raised(low["turn_enu"],1.60),raised(low["start_enu"],1.16),62.),
        shot("52-upper-walkway-approach",raised(up["start_enu"],1.59),raised(upper_station,1.12)),
        shot("52-upper-walkway-look-back",raised(up["turn_enu"],1.60),raised(upper_return,1.12)),
    ]
    args.out.mkdir(exist_ok=True,parents=True)
    (args.out/"views.json").write_text(json.dumps(shots,indent=2)+"\n")
    distances={
        "01_main_hall":separation(market["turn_enu"],outline(plots[1])),
        "52_lower_public_exterior":separation(low["turn_enu"],outline(plots[52])),
        "52_adjacent_upper_walkway":separation(up["turn_enu"],outline(plots[52])),
    }
    distances["52_lower_fixed_approach_floor"]=approach
    (args.out/"folds.json").write_text(json.dumps(distances,indent=2)+"\n")


if __name__=="__main__":
    main()
