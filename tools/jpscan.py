"""Find Japanese text runs in a binary: Shift-JIS (cp932) and UTF-16LE. usage: jpscan.py FILE [min_chars=3] [base_addr]"""
import re, sys

def sjis_runs(d, n=3):
    rx = re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x20-\x7e]){%d,}' % (2 * n))
    for m in rx.finditer(d):
        try: s = m.group().decode('cp932')
        except UnicodeDecodeError: continue
        if sum(1 for c in s if ord(c) > 0x2FFF) >= n: yield m.start(), s

def utf16_runs(d, n=3):
    rx = re.compile(rb'(?:[\x00-\xff][\x30-\x9f]|[\x20-\x7e]\x00){%d,}' % n)
    for m in rx.finditer(d):
        s = m.group()
        if len(s) % 2 or m.start() % 2: continue
        try: t = s.decode('utf-16le')
        except UnicodeDecodeError: continue
        if sum(1 for c in t if 0x3040 <= ord(c) <= 0x9FFF) >= n: yield m.start(), t

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    base = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
    for o, s in sjis_runs(d, n): print(f'sjis  {base + o:#x} {s}')
    for o, s in utf16_runs(d, n): print(f'utf16 {base + o:#x} {s}')
