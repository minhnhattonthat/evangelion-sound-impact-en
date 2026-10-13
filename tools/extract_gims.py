"""Pull every embedded GIM out of work/arc into work/gim/<cpk>/<arc>/<file>_<offset>.gim (+ standalone .gim copies)."""
import glob, os, re, struct, hashlib
seen = {}
for fn in sorted(glob.glob('work/arc/*/*/*.*')):
    parts = fn.replace('\\', '/').split('/'); cp, arc, name = parts[-3], parts[-2], os.path.basename(fn).split('.')[0]
    d = open(fn, 'rb').read()
    for m in re.finditer(rb'MIG\.00\.1PSP', d):
        o = m.start(); ln = 16 + struct.unpack_from('<I', d, o + 0x14)[0]
        g = d[o:o + ln]; h = hashlib.md5(g).hexdigest()
        out = f'work/gim/{cp}/{arc}/{name}_{o:x}.gim'
        os.makedirs(os.path.dirname(out), exist_ok=True); open(out, 'wb').write(g)
        seen.setdefault(h, []).append(out)
print(len(seen), 'unique of', sum(map(len, seen.values())))
