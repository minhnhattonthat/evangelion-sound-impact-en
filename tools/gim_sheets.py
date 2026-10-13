"""Render every GIM under work/arc/<cpk>/<arc>/ into one contact sheet per arc: work/sheets/<cpk>_<arc>.png.
usage: gim_sheets.py [glob-of-arc-dirs]"""
import sys, glob, os; sys.path.insert(0, os.path.dirname(__file__)); import gim
from PIL import Image, ImageDraw
pat = sys.argv[1] if len(sys.argv) > 1 else 'work/gim/*/*'
os.makedirs('work/sheets', exist_ok=True)
for d in sorted(glob.glob(pat)):
    tiles = []
    for fn in sorted(glob.glob(d + '/*.gim')):
        data = open(fn, 'rb').read()
        for i, im in enumerate(gim.parse(data)):
            try: w, h, rows = gim.to_rgba(data, im)
            except Exception as e: continue
            t = Image.frombytes('RGBA', (w, h), b''.join(rows))
            bg = Image.new('RGBA', t.size, (60, 60, 90, 255)); bg.alpha_composite(t)
            tiles.append((os.path.basename(fn)[:3], bg.convert('RGB')))
    if not tiles: continue
    cw = 256; cols = 4; cells = []
    for name, t in tiles:
        s = min(cw / t.width, cw / t.height, 1); t = t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))))
        c = Image.new('RGB', (cw, cw + 12), (20, 20, 20)); c.paste(t, (0, 12)); ImageDraw.Draw(c).text((2, 0), name, fill=(255, 255, 0)); cells.append(c)
    rows = (len(cells) + cols - 1) // cols; per = 4
    for part in range(0, rows, per):
        sh = Image.new('RGB', (cols * cw, min(per, rows - part) * (cw + 12)), (0, 0, 0))
        for k, c in enumerate(cells[part * cols:(part + per) * cols]): sh.paste(c, ((k % cols) * cw, (k // cols) * (cw + 12)))
        sh.save(f'work/sheets/{os.path.basename(os.path.dirname(d))}_{os.path.basename(d)}_{part // per}.png')
