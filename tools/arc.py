"""Game 'ARC\\0' container.
Layout: 'ARC\\0', u32 count, u32 max-unpacked-size, u32 0; entry table (entry 0: size,flags; entry n>0: offset,size,flags);
data blocks at table end, each padded to 4 bytes. flags: low 16 bits = content type, bit 16 = zlib-packed.
Library: parse(bytes) -> [Entry(flags, data, packed)]; build(entries) -> bytes
usage: arc.py FILE.arc [OUTDIR]   (list; with OUTDIR extract as NNN.<type>)"""
import struct, sys, os, zlib
from collections import namedtuple

Entry = namedtuple('Entry', 'flags data packed')   # data = unpacked bytes, packed = original block bytes (or None)

def parse(b):
    assert b[:4] == b'ARC\0', b[:4]
    n = struct.unpack_from('<I', b, 4)[0]
    ents = []; p = 0x10
    sz, f = struct.unpack_from('<II', b, p); ents.append((0, sz, f)); p += 8
    for _ in range(1, n):
        ents.append(struct.unpack_from('<III', b, p)); p += 12
    out = []
    for off, sz, f in ents:
        blk = b[p + off:p + off + sz]
        if f & 0x10000:
            d = zlib.decompressobj(); data = d.decompress(blk)
        else: data = blk
        out.append(Entry(f, data, blk))
    return out

def pack(data, level=9):
    return zlib.compress(data, level)

def build(entries, level=9):
    """entries: [(flags, unpacked_data)] or Entry; reuses Entry.packed when data is unchanged."""
    blocks = []
    for e in entries:
        flags, data = e[0], e[1]
        packed = getattr(e, 'packed', None)
        if flags & 0x10000:
            if packed is not None and zlib.decompress(packed) == data: blk = packed
            else: blk = pack(data, level)
        else: blk = data
        blocks.append((flags, blk + b'\0' * (-len(blk) % 4)))
    n = len(blocks); head = bytearray(b'ARC\0' + struct.pack('<III', n, max(len(e[1]) for e in entries), 0))
    off = 0
    for i, (f, blk) in enumerate(blocks):
        head += struct.pack('<II', len(blk), f) if i == 0 else struct.pack('<III', off, len(blk), f)
        off += len(blk)
    return bytes(head) + b''.join(blk for _, blk in blocks)

if __name__ == '__main__':
    b = open(sys.argv[1], 'rb').read()
    for n, e in enumerate(parse(b)):
        print(n, hex(e.flags), len(e.packed), len(e.data), e.data[:8])
        if len(sys.argv) > 2:
            os.makedirs(sys.argv[2], exist_ok=True); open(f'{sys.argv[2]}/{n:03d}_{e.flags & 0xffff:x}.bin', 'wb').write(e.data)
