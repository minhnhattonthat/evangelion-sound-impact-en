"""Build the English ISO from the original ISO + gfx/ PNG edits + text/ patches.
usage: python tools/build.py [OUT.iso]      (run from the repo root; default build/evangelion-en.iso)

gfx/<cpk>/<arc>/<NNN>_<hexoffset>.png   replaces the GIM that tools/unpack_all.py wrote to work/gim/<cpk>/<arc>/<NNN>_<hexoffset>.gim
                                        (same size and format; indexed images keep their palette unless it fits badly)
text/eboot.tsv                          offset<TAB>english   (byte offsets into the decrypted EBOOT; see tools/eboot.py)
Unchanged files are copied byte for byte; changed ARCs are rebuilt with zlib level 6 (the game's own level)."""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso, cpk, arc, gim
from PIL import Image

ROOT = os.getcwd()
SRC = glob.glob('rom/*.iso')[0]
OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/evangelion-en.iso'
USR = '/PSP_GAME/USRDIR/'

def load_png(path):
    im = Image.open(path).convert('RGBA'); w, h = im.size; b = im.tobytes()
    return w, h, [b[y * w * 4:(y + 1) * w * 4] for y in range(h)]

def main():
    edits = collections.defaultdict(lambda: collections.defaultdict(list))   # cpk -> arc -> [(entry, off, png)]
    for p in sorted(glob.glob('gfx/*/*/*.png')):
        if p.replace(chr(92), '/').startswith(('gfx/PSP_GAME/', 'gfx/raw/')): continue
        cp, a, name = p.replace('\\', '/').split('/')[1:]
        n, off = name[:-4].split('_'); edits[cp][a].append((int(n), int(off, 16), p))
    raw = collections.defaultdict(dict)   # whole-file replacements inside a CPK: gfx/raw/<cpk>/<file name>
    for p in sorted(glob.glob('gfx/raw/*/*')):
        cp, fname = p.replace(chr(92), '/').split('/')[2:]
        raw[cp][fname] = open(p, 'rb').read(); edits[cp]
    with open(SRC, 'rb') as f: files = {p: (lba, ln) for p, lba, ln, _ in iso.listing(f)}
    repl = {}
    os.makedirs('work/tmp', exist_ok=True)
    for cp, arcs in sorted(edits.items()):
        if cp == 'sys': continue
        path = USR + [p for p in files if p.endswith('/' + cp + '.cpk')][0].split(USR)[1]
        lba, ln = files[path]
        with open(SRC, 'rb') as f: f.seek(lba * 2048); cpk_bytes = f.read(ln)
        tmp = f'work/tmp/{cp}.cpk'; open(tmp, 'wb').write(cpk_bytes)
        new = {}
        info, ents = cpk.open_cpk(tmp)
        for a, items in arcs.items():
            if a.endswith('__bin'):   # GIMs inside a plain (non-ARC) file: patch the bytes in place
                e = [x for x in ents if x.name == a[:-5] + '.bin'][0]; d = bytearray(cpk_bytes[e.off:e.off + e.csize])
                for n, off, png in items:
                    g = bytes(d[off:off + 16 + struct.unpack_from('<I', d, off + 0x14)[0]])
                    im = gim.parse(g)[0]; w, h, rows = load_png(png); assert (w, h) == (im.w, im.h), png
                    d[off:off + len(g)] = gim.encode(g, im, rows)
                new[e.name] = bytes(d); continue
            e = [x for x in ents if x.name == a + '.arc'][0]
            es = arc.parse(cpk_bytes[e.off:e.off + e.csize])
            data = {}
            for n, off, png in items:
                d = bytearray(data.get(n, es[n].data))
                g = bytes(d[off:off + 16 + struct.unpack_from('<I', d, off + 0x14)[0]])
                im = gim.parse(g)[0]; w, h, rows = load_png(png)
                assert (w, h) == (im.w, im.h), f'{png}: {w}x{h} but the GIM is {im.w}x{im.h}'
                d[off:off + len(g)] = gim.encode(g, im, rows); data[n] = bytes(d)
            es = [arc.Entry(x.flags, data.get(i, x.data), x.packed if i not in data else None) for i, x in enumerate(es)]
            new[a + '.arc'] = arc.build(es, 6)
        new.update(raw.get(cp, {}))
        repl[path] = cpk.rebuild(tmp, new)
    if 'sys' in edits:   # menu_saveload.arc sits loose in USRDIR/sys
        for a, items in edits['sys'].items():
            path = USR + 'sys/' + a + '.arc'; lba, ln = files[path]
            with open(SRC, 'rb') as f: f.seek(lba * 2048); es = arc.parse(f.read(ln))
            data = {}
            for n, off, png in items:
                d = bytearray(data.get(n, es[n].data)); g = bytes(d[off:off + 16 + struct.unpack_from('<I', d, off + 0x14)[0]])
                im = gim.parse(g)[0]; w, h, rows = load_png(png); assert (w, h) == (im.w, im.h), png
                d[off:off + len(g)] = gim.encode(g, im, rows); data[n] = bytes(d)
            repl[path] = arc.build([arc.Entry(x.flags, data.get(i, x.data), x.packed if i not in data else None) for i, x in enumerate(es)], 6)
    if os.path.exists('gfx/PSP_GAME/PIC1.png'): repl['/PSP_GAME/PIC1.PNG'] = open('gfx/PSP_GAME/PIC1.png', 'rb').read()
    import eboot, sfo
    eboot.main()   # text/eboot.tsv over the decrypted dump -> work/EBOOT.en.elf
    repl['/PSP_GAME/SYSDIR/EBOOT.BIN'] = open('work/EBOOT.en.elf', 'rb').read()
    with open(SRC, 'rb') as f: lba, ln = files['/PSP_GAME/PARAM.SFO']; f.seek(lba * 2048); param = f.read(ln)
    repl['/PSP_GAME/PARAM.SFO'] = sfo.set_str(param, 'TITLE', 'Rebuild of Evangelion -Sound Impact-')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    iso.patch(SRC, OUT, repl)
    print('wrote', OUT, 'with', len(repl), 'changed files:', ', '.join(sorted(p.rsplit('/', 1)[1] for p in repl)))

main()
