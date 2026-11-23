"""Keep licensed photographic references and per-image attribution in the local art study."""
from pathlib import Path
from urllib import request,parse
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,html,re
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
root=Path(__file__).resolve().parent
folder=root/'reference';folder.mkdir(exist_ok=True)
titles=['Shancheng Alley, Chongqing.jpg','山城巷上区.jpg','山城步道——山城巷.jpg','重庆山城步道入口.jpg','出售收购各种物品 - Sell and Purchase All Kinds of Goods - 2015.04 - panoramio.jpg','十八梯 - Shibati Area - 2015.04 - panoramio.jpg','十八梯一楼一底的民居 - panoramio.jpg','十八梯老街 - Old Street in Shibati Area - 2015.04 - panoramio.jpg','重庆十八梯厚慈街 - panoramio.jpg']
def get(url):
    return request.urlopen(request.Request(url,headers={'User-Agent':'ChongqingStreetArtStudy/1.0 (local reference and credit research)'}),timeout=25).read()
def plain(s):return html.unescape(re.sub('<[^>]+>','',s)).strip()
def one(pair):
    i,title=pair
    query={'action':'query','format':'json','titles':'File:'+title,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':960}
    j=json.loads(get('https://commons.wikimedia.org/w/api.php?'+parse.urlencode(query)))
    page=next(iter(j['query']['pages'].values()))
    q=page['imageinfo'][0]; m=q['extmetadata']; field=lambda s:plain(m.get(s,{}).get('value',''))
    src=q.get('thumburl',q['url'])
    try:b=get(src)
    except Exception:b=get(q['url'])
    im=ImageOps.exif_transpose(Image.open(BytesIO(b))).convert('RGB');im.thumbnail((1100,1000))
    fn=f'{i:02d}.jpg';im.save(folder/fn,quality=92)
    return {'id':i,'file':fn,'title':title,'author':field('Artist'),'date':field('DateTimeOriginal'),'license':field('LicenseShortName'),'terms':field('LicenseUrl'),'page':q['descriptionurl'],'photo_url':q['url'],'retrieved_sha256':hashlib.sha256(b).hexdigest(),'local_sha256':hashlib.sha256((folder/fn).read_bytes()).hexdigest(),'modification':'resized for local reference; original aspect ratio'}
def safe(pair):
    try: return one(pair)
    except Exception as e: print(pair,repr(e),flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    items=[x for x in pool.map(safe,enumerate(titles,1)) if x]
(folder/'credits.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
sheet=Image.new('RGB',(1170,3*245),(33,37,38));draw=ImageDraw.Draw(sheet);ft=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
for i,r in enumerate(items):
    im=Image.open(folder/r['file']);im.thumbnail((375,210));x=i%3*390;y=i//3*245
    sheet.paste(im,(x,y));draw.text((x,y+212),f"{r['id']}  {r['title'][:18]}   {r['license']}",font=ft,fill='white')
sheet.save(root/'reference_index.jpg',quality=93)
print('REFERENCES',len(items))

