from pathlib import Path
from PIL import Image
import numpy as np
here=Path(__file__).resolve().parent
dest=here.parents[1]/'project/chongqing_godot_v05/assets/terrace_gardens'
for array,target in [('terrace_normals','normals'),('upper_normals','upper_normals')]:
    Image.fromarray(np.load(here/(array+'.npy'))).save(dest/(target+'.png'))
