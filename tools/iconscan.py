"""Find the orange button icons (circle/cross/triangle/square discs, ~12-16 px) inside UI text images and annotate them.
Library: find_icons(img) -> [(x0, y0, x1, y1)] in reading order; text_rows(img) -> [(y0, y1)] bands of white text.
usage: iconscan.py OUT.png ID [ID...]   (annotated 3x preview: icon numbers in yellow)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw

def find_icons(img, lo=9, hi=24):
    w, h = img.size; px = img.load(); seen = set(); out = []
    def orange(p): return p[3] > 120 and p[0] > 180 and 40 < p[1] < 130 and p[2] < 60
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or not orange(px[x, y]): continue
            st = [(x, y)]; seen.add((x, y)); xs = [x]; ys = [y]
            while st:
                a, b = st.pop()
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (a + dx, b + dy)
                        if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and (orange(px[n]) or (px[n][3] > 120 and sum(px[n][:3]) < 90)):
                            seen.add(n); st.append(n); xs.append(n[0]); ys.append(n[1])
            bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
            if lo <= bw <= hi and lo <= bh <= hi and abs(bw - bh) <= 3: out.append((min(xs), min(ys), max(xs), max(ys)))
    return sorted(out, key=lambda b: (b[1] // 6, b[0]))

def text_rows(img, thr=60):
    px = img.load(); out = []; s = None
    for y in range(img.height + 1):
        on = y < img.height and any(px[x, y][3] > thr and px[x, y][0] > 200 and px[x, y][1] > 200 for x in range(img.width))
        if on and s is None: s = y
        if not on and s is not None: out.append((s, y - 1)); s = None
    return out

if __name__ == '__main__':
    import gen_gfx as g
    out = sys.argv[1]; ids = sys.argv[2:]; tiles = []
    for i in ids:
        o = g.orig(i); ic = find_icons(o); bg = Image.new('RGBA', o.size, (70, 70, 110, 255)); bg.alpha_composite(o)
        z = bg.resize((o.width * 3, o.height * 3), Image.NEAREST).convert('RGB'); d = ImageDraw.Draw(z)
        for k, b in enumerate(ic):
            d.rectangle([b[0] * 3 - 1, b[1] * 3 - 1, b[2] * 3 + 4, b[3] * 3 + 4], outline=(255, 255, 0)); d.text((b[0] * 3, b[1] * 3 - 11), str(k), fill=(255, 255, 0))
        d.text((2, 2), i + f'  icons={len(ic)}', fill=(0, 255, 0)); tiles.append(z)
    W = sum(t.width for t in tiles) + 6 * len(tiles); H = max(t.height for t in tiles)
    sh = Image.new('RGB', (W, H), (0, 0, 0)); x = 0
    for t in tiles: sh.paste(t, (x, 0)); x += t.width + 6
    sh.save(out)
