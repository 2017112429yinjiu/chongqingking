from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,extent
for o in scene.objects:
    if not o.name.startswith(('B_809889623_market_Interior_asset_0_','Soil_bed_central_upper_west_shrub_0','Planted_tree_04_','Planted_tree_12_','N13_PlantingSoil','COL_N13_PlantingRims')):continue
    print('DONOR',o.name,len(o.data.polygons),extent(o),[(s.name) for s in o.material_slots])
