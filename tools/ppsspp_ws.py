"""Minimal stdlib WebSocket client for PPSSPP's debugger API (ws://localhost:PORT/debugger).
usage: ppsspp_ws.py PORT EVENT [JSON-params]   e.g. ppsspp_ws.py 45678 memory.read '{"address":139460608,"size":16}'"""
import socket, base64, os, struct, json, sys

class WS:
    def __init__(self, port, host='127.0.0.1', timeout=30):
        self.s = socket.create_connection((host, port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(f'GET /debugger HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                       f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
        buf = b''
        while b'\r\n\r\n' not in buf: buf += self.s.recv(1)
        assert b' 101 ' in buf.split(b'\r\n')[0], buf
        self.buf = b''; self.ticket = 0

    def _read(self, n):
        while len(self.buf) < n:
            c = self.s.recv(1 << 20)
            if not c: raise EOFError
            self.buf += c
        r, self.buf = self.buf[:n], self.buf[n:]; return r

    def recv(self):
        data = b''
        while True:
            h = self._read(2); op, ln = h[0] & 15, h[1] & 127
            if ln == 126: ln = struct.unpack('>H', self._read(2))[0]
            elif ln == 127: ln = struct.unpack('>Q', self._read(8))[0]
            p = self._read(ln)
            if op == 9: self._send(10, p); continue
            data += p
            if h[0] & 128: break
        return json.loads(data)

    def _send(self, op, p):
        m = os.urandom(4); ln = len(p)
        h = bytes([128 | op]) + (bytes([128 | ln]) if ln < 126 else b'\xfe' + struct.pack('>H', ln) if ln < 65536 else b'\xff' + struct.pack('>Q', ln))
        self.s.sendall(h + m + bytes(b ^ m[i & 3] for i, b in enumerate(p)))

    def call(self, event, **params):
        """Send EVENT, return the reply with the same ticket (other events are dropped)."""
        self.ticket += 1
        self._send(1, json.dumps(dict(event=event, ticket=self.ticket, **params)).encode())
        while True:
            r = self.recv()
            if r.get('ticket') == self.ticket:
                if r['event'] == 'error': raise RuntimeError(r.get('message', r))
                return r

    def mem(self, addr, size):
        return base64.b64decode(self.call('memory.read', address=addr, size=size)['base64'])

if __name__ == '__main__':
    w = WS(int(sys.argv[1])); r = w.call(sys.argv[2], **(json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}))
    print(json.dumps(r)[:4000])
