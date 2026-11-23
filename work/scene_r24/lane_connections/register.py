"""Fit the player's photograph of the editor to surveyed mesh corners and distant landmarks."""
from pathlib import Path
import json,numpy as np,math
here=Path(__file__).resolve().parent
# Surveyed points in Blender east, north, up. The first three describe the last tread.
points=np.array([[28.01331,11.94686,23.50552],[29.98669,13.48171,23.50552],[27.01331,13.23257,23.50552],[27.792,9.36,22.80652],[28.192,9.36,22.80652],[40.,56.,30.64],[46.,54.,30.93]])
pixels=np.array([[880.,482.],[1062.,432.],[700.,456.],[1000.,807.],[1095.,785.],[892.,180.],[1011.,180.]])
strength=np.array([1,1,1,1,1,.55,.55])[:,None]
def project(p, pts):
    pos=p[:3];heading,pitch=p[3:5];f=math.exp(p[5])
    direction=np.array([math.sin(heading)*math.cos(pitch),math.cos(heading)*math.cos(pitch),math.sin(pitch)])
    side=np.array([math.cos(heading),-math.sin(heading),0.]);up=np.cross(side,direction)
    v=pts-pos;d=v@direction
    return np.stack([986.5+f*(v@side)/d,593.-f*(v@up)/d],axis=1),direction
def loss(p):return ((project(p,points)[0]-pixels)*strength).flatten()
p=np.array([26.,5.9,24.3,.3,-.13,math.log(1080.)]);lam=.001
for _ in range(160):
    r=loss(p);jac=np.stack([(loss(p+np.eye(6)[k]*.00001)-r)/.00001 for k in range(6)],axis=1)
    step=np.linalg.solve(jac.T@jac+lam*np.diag(np.diag(jac.T@jac)),jac.T@r)
    if np.linalg.norm(loss(p-step))<np.linalg.norm(r):p-=step;lam=max(lam*.4,1e-9)
    else:lam=min(lam*5,1e9)
pt,dir=project(p,points)
def engine(v):return [float(v[0]),float(v[2]),float(-v[1])]
profile=json.loads((here.parent/'window_life/front_steps/candidate.json').read_text('utf8'))
view={'title':'上院步道 · 东巷接头','position':engine(p[:3]),'target':engine(p[:3]+dir*5),'fov':math.degrees(2*math.atan(593./math.exp(p[5])))}
profile['diagnostic_views']['r24_east_upper_joint']=view
for name,title,pos,target,fov in [('reverse','从东巷看上院步道',(32.3,8.9,24.15),(28.44,12.98,23.35),64),('grate','上院坡地雨水箅',(27.15,8.01,24.17),(27.98,9.5,22.79),49)]:
    profile['diagnostic_views']['r24_east_upper_'+name]={'title':title,'position':engine(pos),'target':engine(target),'fov':fov}
(here/'before.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),'utf8')
(here/'registration.json').write_text(json.dumps({'camera':view,'rms_px':float(np.sqrt(np.mean((pt-pixels)**2))),'approximate_correspondences':list(zip(points.tolist(),pixels.tolist(),pt.tolist()))},ensure_ascii=False,indent=2),'utf8')
print(view,np.round(pt-pixels,2))
