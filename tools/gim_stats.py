"""Index of every unique embedded GIM: work/gim_index.tsv (md5, w, h, fmt, count, first path). Prints size histogram per cpk group."""
import sys, glob, os, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import gim
idx = {}
for fn in sorted(glob.glob('work/gim/*/*/*.gim')):
    d = open(fn, 'rb').read(); h = hashlib.md5(d).hexdigest(); p = fn.replace('\\', '/')
    if h in idx: idx[h][3].append(p); continue
    try: im = gim.parse(d)[0]
    except Exception: continue
    idx[h] = [im.w, im.h, gim.FMT.get(im.fmt, im.fmt), [p]]
with open('work/gim_index.tsv', 'w') as f:
    for h, (w, hh, fmt, ps) in idx.items(): f.write(f'{h}\t{w}\t{hh}\t{fmt}\t{len(ps)}\t{ps[0]}\n')
c = collections.Counter()
for h, (w, hh, fmt, ps) in idx.items(): c[(ps[0].split('/')[2][:2], w, hh)] += 1
for k, v in sorted(c.items(), key=lambda x: -x[1])[:40]: print(v, k)
print(len(idx), 'unique')
