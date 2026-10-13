"""Patch strings in the decrypted EBOOT in place.  usage: eboot.py [IN.elf] [OUT.elf]   (defaults work/EBOOT.dec.elf -> work/EBOOT.en.elf)
text/eboot.tsv: offset<TAB>utf8|sjis<TAB>english. Each string must fit its original NUL-terminated slot (the slot is the original string's
length, plus the zero padding that follows it); the rest is zero-filled. Also checks that the old bytes decode as the claimed encoding."""
import sys, os

def slot(d, off):
    end = d.index(b'\0', off); n = end
    while n < len(d) and d[n] == 0 and n - end < 3: n += 1    # strings are 4-aligned: the zero pad after the terminator is free too
    return end - off, n - off

def main(src='work/EBOOT.dec.elf', dst='work/EBOOT.en.elf', table='text/eboot.tsv'):
    d = bytearray(open(src, 'rb').read()); done = 0
    for ln in open(table, encoding='utf-8'):
        if not ln.strip() or ln.startswith('#'): continue
        off, enc, text = ln.rstrip('\n').split('\t'); off = int(off, 16); text = text.replace('\\n', '\n')
        used, room = slot(d, off); codec = 'utf-8' if enc == 'utf8' else 'cp932'
        d[off:off + used].decode(codec)          # raises if the offset is not a string of that encoding
        new = text.encode(codec)
        if len(new) > room - 1: sys.exit(f'{off:#x}: {len(new)} bytes > {room - 1} available ({text!r})')
        d[off:off + room] = new.ljust(room, b'\0'); done += 1
    open(dst, 'wb').write(d); print(f'{done} strings -> {dst}')

if __name__ == '__main__':
    main(*sys.argv[1:3])
