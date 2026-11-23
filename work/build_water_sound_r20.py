"""Original short running-water loop: filtered noise and decaying droplet oscillations."""
from pathlib import Path
import wave,numpy as np
W=Path(__file__).resolve().parent
rate=24000;n=rate*3
rng=np.random.default_rng(2012)
raw=rng.normal(0,1,n);freq=np.fft.rfftfreq(n,1/rate)
band=(1-np.exp(-(freq/780)**2))*np.exp(-(freq/5900)**2)
bed=np.fft.irfft(np.fft.rfft(raw)*band)
t=np.arange(n)/rate
out=.065*bed*(1+.18*np.sin(2*np.pi*t*2))
for i in range(120):
    start=rng.integers(0,n);f=rng.uniform(650,2250);phase=rng.uniform(0,6.28)
    u=np.arange(1050)/rate
    note=np.sin(2*np.pi*f*u*(1+.6*u)+phase)*np.exp(-u*145)*(1-np.exp(-u*1200))
    out[(start+np.arange(len(u)))%n]+=note*rng.uniform(.035,.13)
path=W/'project/chongqing_godot_v05/assets/lane_r20/rinse.wav'
with wave.open(str(path),'wb') as dest:
    dest.setparams((1,2,rate,n,'NONE',''))
    dest.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
