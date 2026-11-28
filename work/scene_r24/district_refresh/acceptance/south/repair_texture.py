"""Grade the CC0 metal scan for the unpainted steel on hand tools."""
from pathlib import Path
import sys

from PIL import Image, ImageOps


source, output = map(Path,sys.argv[1:])
with Image.open(source) as scan:
    grain = ImageOps.grayscale(scan).resize((512,512),Image.Resampling.LANCZOS)
    # Retain the photographed pitting and tool marks, without the red pigment
    # of the donor paint. The original normal and roughness maps remain in use.
    steel = grain.point([148+round(i*.27) for i in range(256)])
    steel.convert('RGB').save(output,quality=94,subsampling=0)
