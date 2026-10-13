"""MNUF ('FUNM') UI layout files (entry type 6 inside ARCs): object table with sprite positions, sizes and UV rects.
Object k (0x9c bytes at 0x24 + k*0x9c): name[32], pos.xy f32 @+0x48 (sprite centre, screen 480x272), size.wh f32 @+0x64,
uv u0 v0 u1 v1 f32 @+0x80 (fractions of the texture). Objects are in the same order as the embedded GIMs.
Library: objects(bytes) -> [dict]; sprite(cpk, arc, gim_id) -> (w, h, pos) or None   (needs work/ from unpack_all.py)"""
import struct, glob, os

def objects(d):
    assert d[:4] == b'MNUF'
    n = struct.unpack_from('<I', d, 8)[0]; out = []
    for k in range(n):
        o = 0x24 + k * 0x9c
        out.append(dict(off=o, name=d[o:o + 32].split(b'\0')[0].decode('latin1'), pos=struct.unpack_from('<2f', d, o + 0x48),
                        size=struct.unpack_from('<2f', d, o + 0x64), uv=struct.unpack_from('<4f', d, o + 0x80)))
    return out

def sprite(gid):
    """gid = '<cpk>/<arc>/<NNN>_<hexoff>' -> (w, h, (x, y)) of the sprite showing that GIM, assuming objects and GIMs pair in order."""
    cp, arc, name = gid.split('/'); n = int(name.split('_')[0])
    ent = glob.glob(f'work/arc/{cp}/{arc}/{n:03d}_6.bin')
    if not ent: return None
    objs = objects(open(ent[0], 'rb').read())
    gims = sorted(glob.glob(f'work/gim/{cp}/{arc}/{n:03d}_*.gim'), key=lambda p: int(os.path.basename(p).split('_')[-1][:-4], 16))
    ids = [os.path.basename(g)[:-4] for g in gims]
    k = ids.index(name) if name in ids else None
    if k is None or len(objs) != len(gims): return None
    o = objs[k]; return int(o['size'][0]), int(o['size'][1]), o['pos']
