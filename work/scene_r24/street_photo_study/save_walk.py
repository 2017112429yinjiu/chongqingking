from pathlib import Path
import json
from PIL import Image
root=Path(__file__).resolve().parent
motion=root/'motion';data=json.loads((motion/'continuous.json').read_text('utf-8-sig'))
assert data['reached'] and data['max_physics_step_m']<.50
frames=[Image.open(motion/('walk_%03d.jpg'%i)).convert('RGB') for i in range(data['captured'])]
target=root/'走过菜摊.webp'
frames[0].save(target,save_all=True,append_images=frames[1:],duration=67,loop=0,quality=83,method=4)
check=Image.open(target)
assert check.n_frames==data['captured']
print(check.size,check.n_frames)

