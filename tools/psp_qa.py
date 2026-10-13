"""Headless-ish PSP QA driver: boots an ISO in PPSSPP (window hidden), plays a scripted route over PPSSPP's WebSocket
debugger API, takes screenshots, exits with a real code.

  python psp_qa.py GAME.iso --out DIR [--route-str "600 -;3 cross;120 -"] [--route FILE] [--frames N]
                   [--shots 300,900] [--shot-every N] [--smoke] [--fast] [--show] [--emu PPSSPP.exe] [--state F]

Route: "FRAMES KEYS" steps separated by ';' or newlines; FRAMES is emulated 60 Hz frames, KEYS is '-' (nothing) or buttons joined
with '+': cross circle square triangle start select up down left right ltrigger rtrigger. Lines starting with # are comments.
--fast holds Tab (PPSSPP's fast-forward, ~17x) by sending real key events: this needs the PPSSPP window in the foreground
and grabs the keyboard focus for the duration, so leave it off unless you are not typing.
Exit: 0 ok, 2 driver/emulator error, 3 smoke failed (blank final frame), 124 timeout."""
import argparse, base64, ctypes, glob, json, os, re, socket, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ppsspp_ws, winctl

BUTTONS = {'cross', 'circle', 'square', 'triangle', 'start', 'select', 'up', 'down', 'left', 'right', 'ltrigger', 'rtrigger'}
FRAME_US = 1e6 / 60

def parse_route(text):
    steps = []
    text = '\n'.join(l.split('#')[0] for l in text.split('\n'))   # comments first: they may contain ';'
    for ln in re.split(r'[;\n]', text):
        ln = ln.strip()
        if not ln: continue
        n, _, k = ln.partition(' '); k = k.strip() or '-'
        keys = set() if k == '-' else set(x.lower() for x in k.split('+'))
        bad = keys - BUTTONS
        if bad: sys.exit(f'unknown button(s) {bad}')
        steps.append((int(n), keys))
    return steps

def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p

def find_emu(arg):
    for c in [arg, os.environ.get('PPSSPP')] + glob.glob('tools/**/PPSSPPWindows64.exe', recursive=True) + glob.glob('../*/tools/**/PPSSPPWindows64.exe', recursive=True):
        if c and os.path.exists(c): return os.path.abspath(c)
    sys.exit('PPSSPPWindows64.exe not found: pass --emu or set PPSSPP')

class Run:
    def __init__(self, emu, iso, out, show=False, state=None, memstick=None, extra=()):
        self.out = out; os.makedirs(out, exist_ok=True)
        self.port = free_port()
        ms = memstick or os.path.join(os.path.dirname(emu), 'memstick')
        cmd = [emu, f'--memstick={ms}', f'--debugger={self.port}', f'--log={os.path.abspath(out)}/ppsspp.log']
        if state: cmd.append(f'--state={state}')
        cmd += list(extra)
        cmd.append(os.path.abspath(iso))
        self.p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ws = None; t0 = time.time()
        while time.time() - t0 < 30:
            try: self.ws = ppsspp_ws.WS(self.port, timeout=30); break
            except OSError: time.sleep(0.2)
        if not self.ws: raise RuntimeError('debugger port never opened')
        t0 = time.time()
        while time.time() - t0 < 60:   # wait for the game to be running
            if self.ws.call('game.status')['game']: break
            time.sleep(0.2)
        else: raise RuntimeError('game did not start')
        self.hwnd = None
        for _ in range(50):
            self.hwnd = winctl.main_window(self.p.pid)
            if self.hwnd: break
            time.sleep(0.1)
        if self.hwnd and not show: winctl.show(self.hwnd, 'hide')
        self.keys = set(); self.fast = False; self.show = show

    def us(self): return self.ws.call('cpu.status')['us']
    def frame(self): return int(self.us() / FRAME_US)

    def pause(self):
        self.ws._send(1, b'{"event":"cpu.stepping","ticket":9999}')
        while self.ws.recv().get('event') == 'cpu.stepping': break

    def resume(self):
        self.ws._send(1, b'{"event":"cpu.resume","ticket":9998}')
        for _ in range(20):
            r = self.ws.recv()
            if r.get('event') == 'cpu.resume': break

    def shot(self, name):
        self.pause()
        try: r = self.ws.call('gpu.buffer.screenshot')
        finally: self.resume()
        data = base64.b64decode(r['uri'].split(',')[1])
        open(os.path.join(self.out, name), 'wb').write(data); return os.path.join(self.out, name)

    def press(self, keys):
        if keys == self.keys: return
        self.ws.call('input.buttons.send', buttons={k: (k in keys) for k in BUTTONS}); self.keys = set(keys)

    def set_fast(self, on):
        if on == self.fast or not self.hwnd: return
        u = ctypes.windll.user32
        if on: u.ShowWindow(self.hwnd, 4); u.SetForegroundWindow(self.hwnd); time.sleep(0.3)
        u.keybd_event(9, 0x0F, 0 if on else 2, 0); self.fast = on

    def key_vk(self, vk, hold=0.15):
        """Real keyboard event to the PPSSPP window (needs focus; used for save-state hotkeys)."""
        u = ctypes.windll.user32; u.ShowWindow(self.hwnd, 9); time.sleep(0.5)
        u.keybd_event(0x12, 0, 0, 0); u.keybd_event(0x12, 0, 2, 0)   # an Alt tap lets SetForegroundWindow through
        u.SetForegroundWindow(self.hwnd); time.sleep(0.5)
        sc = u.MapVirtualKeyW(vk, 0); u.keybd_event(vk, sc, 0, 0); time.sleep(hold); u.keybd_event(vk, sc, 2, 0); time.sleep(0.3)
        if self.hwnd and not self.show: winctl.show(self.hwnd, 'hide')

    def save_state(self, dest):
        import shutil
        d = os.path.join(os.path.dirname(find_emu(None)), 'memstick', 'PSP', 'PPSSPP_STATE'); before = set(glob.glob(d + '/*.ppst'))
        self.key_vk(0x71); time.sleep(1.5)   # F2 = save state to the current slot
        new = [f for f in glob.glob(d + '/*.ppst') if f not in before or os.path.getmtime(f) > time.time() - 10]
        if not new: raise RuntimeError('F2 did not produce a .ppst')
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True); shutil.copyfile(max(new, key=os.path.getmtime), dest)

    def close(self):
        try: self.set_fast(False)
        except Exception: pass
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.p.pid)], capture_output=True)

def blank(png):
    """True when the screenshot is a single flat colour (black screen, never rendered)."""
    from PIL import Image
    im = Image.open(png).convert('RGB').resize((48, 27)); lo, hi = im.getextrema()[0], None
    ex = im.getextrema(); return all(a == b or b - a < 6 for a, b in ex)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso'); ap.add_argument('--out', required=True)
    ap.add_argument('--route'); ap.add_argument('--route-str'); ap.add_argument('--frames', type=int)
    ap.add_argument('--shots', default=''); ap.add_argument('--shot-every', type=int, default=0)
    ap.add_argument('--smoke', action='store_true'); ap.add_argument('--fast', action='store_true'); ap.add_argument('--show', action='store_true')
    ap.add_argument('--save-state', help='write the PPSSPP save state (slot 1) to this file at the end of the route'); ap.add_argument('--emu'); ap.add_argument('--emu-arg', action='append', default=[], help='extra PPSSPP argument, e.g. -d for debug logging'); ap.add_argument('--state'); ap.add_argument('--timeout', type=int, default=600)
    a = ap.parse_args()
    steps = parse_route(open(a.route).read() if a.route else a.route_str or '')
    total = sum(n for n, _ in steps)
    frames = a.frames or total or 600
    shots = sorted(int(x) for x in a.shots.split(',') if x)
    run = None; code = 0; t_start = time.time()
    try:
        run = Run(find_emu(a.emu), a.iso, a.out, a.show, a.state, extra=a.emu_arg)
        base = run.frame(); log = open(os.path.join(a.out, 'log.txt'), 'w'); si = 0; nshots = 0; last_ev = -1
        edges = []; acc = 0
        for n, k in steps: edges.append((acc, acc + n, k)); acc += n
        if a.fast: run.set_fast(True)
        while True:
            if time.time() - t_start > a.timeout: code = 124; break
            f = run.frame() - base
            keys = next((k for lo, hi, k in edges if lo <= f < hi), set())
            run.press(keys)
            while si < len(shots) and f >= shots[si]:
                run.shot(f'f{shots[si]:06d}.png'); nshots += 1; si += 1
            if a.shot_every and f // a.shot_every != last_ev and f > 0:
                last_ev = f // a.shot_every; run.shot(f'f{f:06d}.png'); nshots += 1
            if f >= frames: break
            time.sleep(0.02)
        if code == 0:
            run.press(set()); run.set_fast(False)
            if a.save_state: run.save_state(a.save_state)
            fin = run.shot('final.png'); log.write(f'final frame {run.frame() - base}\n'); log.close()
            if a.smoke and blank(fin): code = 3
        print(f'exit {code}  shots {nshots}  final {"yes" if os.path.exists(os.path.join(a.out, "final.png")) else "no"}  '
              f'{time.time() - t_start:.1f}s for {frames} frames  dir {a.out}')
    except Exception as e:
        print('driver error:', e); code = 2
    finally:
        if run: run.close()
    sys.exit(code)

if __name__ == '__main__':
    main()
