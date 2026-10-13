"""List/extract files of an ISO9660 image (PSP UMD). usage: isols.py ISO [-x OUTDIR]"""
import struct, sys, os

def read_dir(f, lba, size, path, out):
    f.seek(lba * 2048); data = f.read(size); i = 0
    while i < size:
        n = data[i]
        if n == 0:
            i = (i // 2048 + 1) * 2048; continue
        rec = data[i:i + n]; i += n
        loc, ln = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
        flags = rec[25]; nl = rec[32]; name = rec[33:33 + nl]
        if name in (b'\x00', b'\x01'): continue
        name = name.decode('latin1').split(';')[0]
        p = path + '/' + name
        if flags & 2: read_dir(f, loc, ln, p, out)
        else: out.append((p, loc, ln))

def listing(f):
    f.seek(16 * 2048); pvd = f.read(2048)
    root = pvd[156:190]
    lba, size = struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0]
    out = []; read_dir(f, lba, size, '', out); return out

if __name__ == '__main__':
    iso = sys.argv[1]
    with open(iso, 'rb') as f:
        files = listing(f)
        if '-x' in sys.argv:
            d = sys.argv[sys.argv.index('-x') + 1]
            for p, lba, ln in files:
                dst = d + p; os.makedirs(os.path.dirname(dst), exist_ok=True)
                f.seek(lba * 2048); open(dst, 'wb').write(f.read(ln))
        else:
            for p, lba, ln in files: print(f'{lba:8d} {ln:11d} {p}')
