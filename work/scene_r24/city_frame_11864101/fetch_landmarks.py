from pathlib import Path
from urllib import request,parse
import json
root=Path(__file__).resolve().parent
q='[out:json][timeout:18];(nwr["name"~"人民解放纪念碑|解放碑|朝天门广场|东水门长江大桥"](29.55,106.572,29.582,106.603););out geom;'
for host in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
    try:
        url=host+'?'+parse.urlencode({'data':q})
        with request.urlopen(request.Request(url,headers={'User-Agent':'Chongqing district model alignment study'}),timeout=24) as r:
            data=json.load(r)
        if data.get('elements'):
            (root/'landmarks_osm.json').write_text(json.dumps(data,ensure_ascii=False),encoding="utf8")
            print([(e['type'],e['id'],e['tags'].get('name')) for e in data['elements']][:55])
            break
    except Exception as exc:print(repr(exc))

