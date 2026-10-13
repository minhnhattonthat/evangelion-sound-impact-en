"""One GIM with a labelled pixel grid, for reading coordinates. usage: gridgim.py ID OUT.png [zoom=3] [step=20]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import gen_gfx as g
i, out = sys.argv[1], sys.argv[2]; z = int(sys.argv[3]) if len(sys.argv) > 3 else 3; st = int(sys.argv[4]) if len(sys.argv) > 4 else 20
o = g.orig(i); bg = Image.new('RGBA', o.size, (70, 70, 110, 255)); bg.alpha_composite(o)
im = bg.resize((o.width * z, o.height * z), Image.NEAREST).convert('RGB'); d = ImageDraw.Draw(im)
for x in range(0, o.width, st): d.line([(x * z, 0), (x * z, im.height)], fill=(0, 255, 255)); d.text((x * z + 2, 2), str(x), fill=(255, 255, 0))
for y in range(0, o.height, st): d.line([(0, y * z), (im.width, y * z)], fill=(0, 255, 0)); d.text((2, y * z + 2), str(y), fill=(255, 255, 0))
im.save(out)
