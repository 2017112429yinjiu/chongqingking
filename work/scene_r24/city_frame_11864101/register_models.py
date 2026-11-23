"""Fit a non-reflecting or reflecting 2D similarity using unique native mesh topology and independent holdouts."""
import json,itertools
from collections import defaultdict
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent
old=root.parent/"chaotianmen_9644040"
def features(folder):
    table=defaultdict(list)
    for r in json.loads((folder/"bounds.json").read_bytes()):
        if r[2]>=60:
            table[tuple(r[2:4])].append(r)
    return {k:v[0] for k,v in table.items() if len(v)==1}
def center(r):
    return (np.array(r[5])+r[6])/2
a,b=features(root),features(old)
keys=sorted(a.keys() & b.keys())
p=np.array([center(a[k]) for k in keys]); q=np.array([center(b[k]) for k in keys])*.01
P=p[:,0]+1j*p[:,1]; Q=q[:,0]+1j*q[:,1]
train=np.arange(len(P))%4!=0
valid=np.full(len(P),True)
best=None
for mirror in (False,True):
    src=P.conjugate() if mirror else P
    for i,j in itertools.combinations(np.where(train)[0],2):
        if abs(src[j]-src[i])<40:continue
        m=(Q[j]-Q[i])/(src[j]-src[i])
        t=Q[i]-m*src[i]
        e=np.abs(m*src+t-Q)
        n=int(((e<6)&train).sum())
        qual=(n,-np.median(np.minimum(e[train],12)))
        if best is None or qual>best[0]:best=(qual,m,t,mirror)
_,m,t,mirror=best
src=P.conjugate() if mirror else P
for _ in range(3):
    e=abs(src*m+t-Q)
    ok=(e<6)&train
    A=np.stack([src[ok],np.ones(ok.sum())],axis=1)
    m,t=np.linalg.lstsq(A,Q[ok],rcond=None)[0]
e=abs(src*m+t-Q)
keep=e<6
dz=q[keep,2]-p[keep,2]*abs(m)
out=dict(new_to_old_native_metres=dict(multiplier=[m.real,m.imag],offset=[t.real,t.imag],conjugate=mirror,vertical_offset=float(np.median(dz))),threshold=6,train_inliers=int(sum(keep&train)),test_inliers=int(sum(keep&~train)),candidates=len(P),holdout_candidates=int(sum(~train)),pairs=[dict(white_node=a[k][0],river_node=b[k][0],xy_error=round(float(e[i]),3),old_m=q[i].round(3).tolist(),partition="train" if train[i] else "holdout") for i,k in enumerate(keys) if keep[i]])
(root/"registration.json").write_text(json.dumps(out,indent=2),encoding="utf8")
print(str({k:v for k,v in out.items() if k!="pairs"}))
print("inlier bounds",p[keep].min(0),p[keep].max(0),"residual",np.percentile(e[keep],[50,90,100]),"dz",np.percentile(dz,[0,50,100]))

