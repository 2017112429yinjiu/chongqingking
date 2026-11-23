"""Pin the exact CC0 source files used for the district's weather and masonry."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,urllib.request,time

out=Path(__file__).resolve().parent/'assets_incoming/district_r21'
out.mkdir(exist_ok=True)
def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ChongqingDistrict local art research/1.0'}),timeout=40) as response:return response.read()
        except OSError:
            if attempt==2:raise
            time.sleep(1)
def fetch(asset,maps):
    spec=json.loads(get('https://api.polyhaven.com/files/'+asset))
    info=json.loads(get('https://api.polyhaven.com/info/'+asset))
    src={'asset':asset,'source':'https://polyhaven.com/a/'+asset,'license':'CC0-1.0','terms':'https://polyhaven.com/license','authors':info['authors'],'dimensions_cm':info.get('dimensions'),'attribution':'Voluntary. Commercial use and redistribution permitted.','files':[]}
    folder=out/asset;folder.mkdir(exist_ok=True)
    (folder/'api_files.json').write_text(json.dumps(spec),encoding='utf8')
    def one(key):
        fmt='hdr' if key=='hdri' else 'jpg'
        aliases={'diff':['diff','Diffuse','color','col','albedo'],'rough':['rough','Rough','roughness','arm']}
        lookup={k.lower():k for k in spec}
        label=next(lookup[k.lower()] for k in aliases.get(key,[key]) if k.lower() in lookup)
        f=spec[label]['2k'][fmt];dst=folder/f['url'].split('/')[-1]
        data=dst.read_bytes() if dst.exists() else get(f['url'])
        assert hashlib.md5(data).hexdigest()==f['md5']
        dst.write_bytes(data)
        return {'map':key,'api_key':label,'file':dst.name,'url':f['url'],'upstream_md5':f['md5'],'sha256':hashlib.sha256(data).hexdigest()}
    with ThreadPoolExecutor(3) as pool:src['files']=list(pool.map(one,maps))
    (folder/'PROVENANCE.json').write_text(json.dumps(src,indent=2,ensure_ascii=False),encoding='utf8')
    print(asset,src['authors'],flush=True)
if __name__=='__main__':
    with ThreadPoolExecutor(3) as pool:
        jobs=[pool.submit(fetch,name,['diff','nor_gl','rough']) for name in ['mossy_stone_wall','sandstone_cracks']]
        jobs.append(pool.submit(fetch,'kloofendal_28d_misty_puresky',['hdri']))
        for job in jobs:job.result()
