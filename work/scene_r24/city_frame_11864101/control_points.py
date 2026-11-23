from pathlib import Path
from urllib import request
from concurrent.futures import ThreadPoolExecutor
import json
root=Path(__file__).resolve().parent
def fetch(way):
    for host in ["https://api.openstreetmap.org","https://www.openstreetmap.org"]:
        try:
            url=f"{host}/api/0.6/way/{way}/full.json"
            with request.urlopen(request.Request(url,headers={"User-Agent":"district art alignment"}),timeout=12) as f: data=json.load(f)
            (root/f"osm_way_{way}.json").write_text(json.dumps(data,ensure_ascii=False),encoding="utf8")
            print(way,len(data["elements"]),flush=True)
            return
        except Exception as exc:print(way,repr(exc),flush=True)
with ThreadPoolExecutor() as pool:list(pool.map(fetch,[589752618,230583762]))

