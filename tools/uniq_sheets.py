"""Contact sheets of the UNIQUE embedded GIMs (md5-deduped over work/gim), grouped by arc-name regex.
usage: uniq_sheets.py REGEX OUTPREFIX [cell=200] [cols=6] [rows=5] [skip-regex]   e.g. uniq_sheets.py 'result' work/sheets/u_result
Cell label = cpk/arc/file; the id is what to open with gim.py."""
import sys, glob, os, re, hashlib
sys.path.insert(0, os.path.dirname(__file__)); import gim
from PIL import Image, ImageDraw

rx, prefix = re.compile(sys.argv[1]), sys.argv[2]
cell = int(sys.argv[3]) if len(sys.argv) > 3 else 200
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
rows = int(sys.argv[5]) if len(sys.argv) > 5 else 5
skip = re.compile(sys.argv[6]) if len(sys.argv) > 6 else None   # regex on 'path WxH'
seen, tiles = set(), []
for fn in sorted(glob.glob('work/gim/*/*/*.gim')):
    p = fn.replace('\\', '/')
    if not rx.search(p): continue
    data = open(fn, 'rb').read(); h = hashlib.md5(data).hexdigest()
    if h in seen: continue
    seen.add(h)
    try: im = gim.parse(data)[0]; w, hh, px = gim.to_rgba(data, im)
    except Exception: continue
    t = Image.frombytes('RGBA', (w, hh), b''.join(px)); bg = Image.new('RGBA', t.size, (70, 70, 110, 255)); bg.alpha_composite(t)
    if skip and skip.search(p + f' {w}x{hh}'): continue
    if os.path.exists('gfx/' + p.split('work/gim/')[1].replace('.gim', '.png')) and not os.environ.get('ALL'): continue   # already translated
    tiles.append(('/'.join(p.split('/')[-3:]).replace('.gim', '') + f' {w}x{hh}', bg.convert('RGB')))
n = cols * rows
for s in range(0, len(tiles), n):
    sh = Image.new('RGB', (cols * cell, rows * (cell + 12)), (0, 0, 0)); dr = ImageDraw.Draw(sh)
    for k, (name, t) in enumerate(tiles[s:s + n]):
        sc = min(cell / t.width, cell / t.height, 4); t = t.resize((max(1, int(t.width * sc)), max(1, int(t.height * sc))))
        x, y = (k % cols) * cell, (k // cols) * (cell + 12); sh.paste(t, (x, y + 12)); dr.text((x + 1, y), name[-34:], fill=(255, 255, 0))
    sh.save(f'{prefix}_{s // n}.png')
print(len(tiles), 'unique ->', (len(tiles) + n - 1) // n, 'sheets')
