from pathlib import Path
from html.parser import HTMLParser
import urllib.request,html,json,hashlib
root=Path(__file__).resolve().parent/'assets_incoming/100style'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.href=None;self.text='';self.links={}
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.href=dict(attrs).get('href');self.text=''
    def handle_data(self,data):
        if self.href:self.text+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.href:self.links[self.text.strip()]=html.unescape(self.href);self.href=None
p=Links();p.feed((root/'source_license_page.html').read_text(encoding='utf-8'))
files=[]
for name in ['Neutral_ID.bvh','Neutral_FW.bvh','Frame_Cuts.csv']:
    url=p.links[name];request=urllib.request.Request(url,headers={'User-Agent':'ChongqingGameAssetResearch/1.0'})
    if (root/name).exists():data=(root/name).read_bytes()
    else:
        with urllib.request.urlopen(request,timeout=45) as response:data=response.read()
    assert not data.lstrip().lower().startswith(b'<!doctype html'),name
    if name.endswith('.bvh'):assert data.lstrip().startswith(b'HIERARCHY'),name
    (root/name).write_bytes(data)
    files.append({'name':name,'source_url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    print('DOWNLOADED',name,len(data),flush=True)
(root/'LICENSE_NOTICE.txt').write_text('The 100STYLE Dataset - Ian Mason\nCC BY 4.0: https://creativecommons.org/licenses/by/4.0/\nSource: https://www.ianxmason.com/100style/\nCommercial use, sharing and adaptations are permitted under this license. Retain credit and license link and identify modifications. No endorsement is implied.\nOriginal BVH files retained; see PROVENANCE.json for exact hashes and later build records for retargeting.\n',encoding='utf-8')
(root/'PROVENANCE.json').write_text(json.dumps({'dataset':'100STYLE','author':'Ian Mason','source':'https://www.ianxmason.com/100style/','license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','required_credit':'The 100STYLE Dataset - Ian Mason','modifications':'Not yet retargeted or integrated. Preserve original BVH and record later trims/retargets.','files':files},indent=2))
