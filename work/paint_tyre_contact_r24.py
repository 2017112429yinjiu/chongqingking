"""A soft, metre-scaled chassis and four tyre contact lobes for local road projection."""
from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parent/'scene_r24/assets/tyre_contact.png'
z,x=np.mgrid[-2.6:2.6:256j,-1.25:1.25:160j]
body=np.exp(-1.6*((x/.96)**4+(z/2.22)**6))
alpha=.47*body
for axle in [-1.32,1.31]:
    for wheel in [-.775,.775]:
        alpha+=.43*np.exp(-((x-wheel)/.17)**2-((z-axle)/.31)**2)
rgba=np.zeros((256,160,4),dtype='uint8')
rgba[:,:,:3]=(28,32,32);rgba[:,:,3]=np.uint8(np.minimum(.93,alpha)*255)
Image.fromarray(rgba).save(p)

