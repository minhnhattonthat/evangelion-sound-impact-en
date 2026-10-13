"""Unpack the whole disc: ISO -> work/iso, CPK -> work/cpk/<cpk>/, ARC -> work/arc/<cpk>/<arc>/NNN_<type>.bin,
embedded GIMs -> work/gim/<cpk>/<arc>/NNN_<offset>.gim.  usage: unpack_all.py [ISO]  (run from the repo root)"""
import sys, glob, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import isols, cpk, arc

iso = sys.argv[1] if len(sys.argv) > 1 else glob.glob('rom/*.iso')[0]
with open(iso, 'rb') as f:
    for p, lba, ln in isols.listing(f):
        if p.endswith('.cpk') or ln < 4_000_000:
            d = 'work/iso' + p; os.makedirs(os.path.dirname(d), exist_ok=True); f.seek(lba * 2048); open(d, 'wb').write(f.read(ln))

def put(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, 'wb').write(data)

def do_arc(cname, aname, b):
    for n, e in enumerate(arc.parse(b)):
        t = e.flags & 0xffff
        put(f'work/arc/{cname}/{aname}/{n:03d}_{t:x}.bin', e.data)
        for m in re.finditer(rb'MIG\.00\.1PSP', e.data):
            o = m.start(); ln = 16 + struct.unpack_from('<I', e.data, o + 0x14)[0]
            put(f'work/gim/{cname}/{aname}/{n:03d}_{o:x}.gim', e.data[o:o + ln])

def do_raw(cname, fname, b):
    """GIMs embedded in a plain (non-ARC) file: written as <cpk>/<file>__bin/000_<offset>.gim"""
    for m in re.finditer(rb'MIG\.00\.1PSP', b):
        o = m.start(); ln = 16 + struct.unpack_from('<I', b, o + 0x14)[0]
        put(f'work/gim/{cname}/{fname[:-4]}__bin/000_{o:x}.gim', b[o:o + ln])

for c in sorted(glob.glob('work/iso/PSP_GAME/USRDIR/*/*.cpk')):
    cname = os.path.basename(c)[:-4]
    info, ents = cpk.open_cpk(c)
    with open(c, 'rb') as f:
        for e in ents:
            if e.name.endswith(('.pmf', '.awb', '.acb')): continue
            f.seek(e.off); data = f.read(e.csize)
            put(f'work/cpk/{cname}/{e.name}', data)
            if e.name.endswith('.arc'): do_arc(cname, e.name[:-4], data)
            elif e.name.endswith('.bin'): do_raw(cname, e.name, data)
do_arc('sys', 'menu_saveload', open('work/iso/PSP_GAME/USRDIR/sys/menu_saveload.arc', 'rb').read())
