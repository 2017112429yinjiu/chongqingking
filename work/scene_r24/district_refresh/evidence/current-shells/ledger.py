"""Join normal-scene shell presence to the existing independent site ledger."""
import argparse
import csv
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

# These entries concern the remaining shell and the current public walking limit.
# Site evidence, photo sources and the independently published walking results
# are copied from the dated plots.tsv columns beside these short status notes.
RETAINED={
    0: ('玩法保留，公共边已改','悬崖公区与既有修车动线已证。原框仍承担玩法，现场修理业态与内件未证。'),
    1: ('玩法保留，公共边已改','保留正常摊主交接和 201 路线。街脚能见，实际屋址及经营用途未证。'),
    12: ('公共边已改，旧屋仍加载','公开步带实测停在瓦檐柱间外约 0.86 米。门后及与收藏市场的归属未证。'),
    22: ('公共边已改，旧屋仍加载','已换公共灰铺和花池。旧屋只按外缘观察，后墙及楼门未证。'),
    26: ('公共边已走，墙脚被遮','街肩可到原折点并返。正面树下墙脚欠缺，南侧柱组属于邻楼观测。'),
    30: ('公共边已改，屋址待证','源道图可证西坡公共栈道，图内屋脚与楼门无法归到旧壳。'),
    31: ('公共边已改，屋址待证','独立核到西坡上缘公共路线。树冠后建筑和墙脚须反向地面控制。'),
    34: ('公共边已改，屋址待证','墙与院口可见，三个航片点均见长灰顶。缺独立反向墙脚，保留后排。'),
    35: ('公共边已改，屋址待证','公开边能走，小顶与相邻大顶未分清，缺可见下层墙脚。'),
    40: ('公共边已改，屋址待证','公开边缘已走，实际楼门、窗下墙脚和后界待核。'),
    41: ('公共边已改，墙后被遮','砌墙、湿痕、方孔及展示栏可见。上下层区分，墙后校舍未归属旧室。'),
    42: ('证据相近，墙脚与门未证','与 OSM 809889635 有交叠。门址、共墙及街面支撑未独立核齐。'),
    43: ('玩法后梯保留，屋址待证','后梯历史回归有记录，无 809889635 叠合；地面照片无法证实当前门牌。'),
    45: ('公开部分已改，树池与旧壳确有冲突','两同址眼把树根和硬铺落在旧轮廓内。候选根部实测有旧框架及围护；白牌墩旁已做灰铺收边。门后与共墙未知。'),
    46: ('公共边已改，旧屋仍加载','已走下坡公开边和白牌墩。低侧店边可见，白牌框、石帽和接地灰铺已修。住户界限及独立楼脚待证。'),
    49: ('公共边已改，屋址待证','有证外栈道与旧中心相距约9米。坡脚屋址和门口仍被植被遮断。'),
    52: ('两层公区已走，屋址待证','高步道、低街分开实测，外折点离旧轮廓约6.65米。照片未定位旧屋墙脚。'),
    53: ('石梯已改，旧屋仍加载','保留既有玩家石梯与门槛；地表断面通过，住户编号及室内未证。'),
    54: ('共用巷已走，屋址关系待证','保留既有玩法，已把停车外墙与独立桥墩分别定位。车库整体轮廓尚待查。'),
    56: ('几何冲突保留待核','现有正门线路有阻挡，实际共用巷可往返。近车库整体墙脚和标高未证。'),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runtime',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    scene=json.loads(args.runtime.read_text())
    named={int(float(k)):v for k,v in scene['named'].items()}
    shell={pid for pid,parts in named.items() if any(row['visible'] and row['name'].startswith('COL_Outer500_Frame_') for row in parts)}
    with (HERE.parent/'plots.tsv').open(encoding='utf-8-sig') as f:
        original=list(csv.DictReader(f,delimiter='\t'))
    path=args.output
    with path.open('w',encoding='utf-8',newline='') as f:
        out=csv.writer(f,delimiter='\t',lineterminator='\n')
        out.writerow(['地块','实际试作框架','旧共享外壳最低命中数','现存可见归属对象','当前状态','现有公共界线与仍缺证据',
                      '地图与控制点','同址照片可证','原已验走线','出处和机位'])
        for row in original:
            if not row['编号'].isdigit():
                continue
            pid=int(row['编号']); parts=[x['name'] for x in named.get(pid,[]) if x['visible']]
            hit=scene['matches'].get(str(pid),0)
            if pid in shell:
                status,detail=RETAINED.get(pid,("旧屋仍加载，公区未分类",row["待核事项"]))
            elif pid==2:
                status,detail='旧屋已退役，保留院落对象','独立框架、旧共享壳均无命中。两个院落对象仍加载，茶摊与取送仍在。'
            elif pid not in named:
                status,detail='历史保留点或未实例化','源布局没有可加载的该号独立旧壳。'
            else:
                status,detail='独立旧壳已退役',row['待核事项']
            out.writerow([row['编号'],'有' if pid in shell else '无',hit,' | '.join(parts),status,detail,
                          row['地图与实测空间证据'],row['同址照片能支持的判断'],row['实际往返'],row['原始证据或出处']])
    print('visible frames',len(shell),'normal layout',len(named),'ledger ids',sum(r['编号'].isdigit() for r in original))


if __name__=='__main__':
    main()
