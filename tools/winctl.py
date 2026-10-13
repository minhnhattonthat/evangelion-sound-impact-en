"""Windows helpers for driving the PPSSPP window: find by pid, hide/show/minimize, post key down/up (no focus needed).
usage: winctl.py PID hide|show|min|keydown VK|keyup VK|title"""
import ctypes, sys
from ctypes import wintypes
u = ctypes.windll.user32
WM_KEYDOWN, WM_KEYUP = 0x100, 0x101
SW = {'hide': 0, 'show': 5, 'min': 6, 'restore': 9, 'noact': 4}

def find(pid):
    out = []
    cb = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(lambda h, _: (out.append(h) if _pid(h) == pid and u.GetWindow(h, 4) == 0 else None) or True)
    u.EnumWindows(cb, 0)
    return out

def _pid(h):
    p = wintypes.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(p)); return p.value

def title(h):
    b = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, b, 256); return b.value

def main_window(pid):
    ws = [h for h in find(pid) if title(h).startswith('PPSSPP')]
    return ws[0] if ws else None

def show(h, how): u.ShowWindow(h, SW[how])

def key(h, vk, down=True):
    sc = u.MapVirtualKeyW(vk, 0)
    u.PostMessageW(h, WM_KEYDOWN if down else WM_KEYUP, vk, 1 | (sc << 16) | (0 if down else 0xC0000000))

if __name__ == '__main__':
    pid = int(sys.argv[1]); h = main_window(pid); cmd = sys.argv[2]
    if cmd == 'title': print(h, title(h))
    elif cmd in SW: show(h, cmd)
    elif cmd == 'keydown': key(h, int(sys.argv[3], 0))
    elif cmd == 'keyup': key(h, int(sys.argv[3], 0), False)
