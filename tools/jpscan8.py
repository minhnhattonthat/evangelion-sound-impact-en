"""Japanese UTF-8 runs in a binary. usage: jpscan8.py FILE [min_chars=2] [base_addr]"""
import re, sys
d = open(sys.argv[1], 'rb').read(); n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
base = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
rx = re.compile(rb'(?:[\xe3-\xe9][\x80-\xbf][\x80-\xbf]|[\x20-\x7e\n]){%d,}' % (n + 1))
for m in rx.finditer(d):
    try: s = m.group().decode('utf-8')
    except UnicodeDecodeError: continue
    if sum(1 for c in s if ord(c) > 0x2FFF) >= n: print(f'{base + m.start():#x} {s!r}')
