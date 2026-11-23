import bpy,numpy as np,json
from pathlib import Path
W=Path(__file__).resolve().parent
p=W/'assets_incoming/r19_sky/kloofendal_overcast_puresky_2k.hdr'
im=bpy.data.images.load(str(p));a=np.asarray(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[::-1,:,:3]
l=a@np.array([.2126,.7152,.0722]);v,u=np.unravel_index(np.argmax(l[:im.size[1]//2]),l[:im.size[1]//2].shape)
report={'size':list(im.size),'max_rgb':float(a.max()),'brightest_uv':[(float(u)+.5)/im.size[0],(float(v)+.5)/im.size[1]],'elevation_deg':90.-180.*(v+.5)/im.size[1],'unrotated_yaw_deg':180.-360.*(u+.5)/im.size[0],'note':'Broad brightest cloud location, not a sharp measured solar disk. Low direct-light contribution is an art approximation.'}
(W/'assets_incoming/r19_sky/measurement.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
