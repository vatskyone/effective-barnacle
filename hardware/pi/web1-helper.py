#!/usr/bin/env python3
"""WEB-1 helper for the physical WEB-1 (Raspberry Pi Compute Module 5).

It replaces `python3 -m http.server`: it serves WEB-1 on http://localhost:8000 (and hw.html at /hw.html), and it gives
the page what a browser cannot do on its own:

  GET  /api/ping              is the helper there (the page turns its device features on)
  GET  /api/power             battery from the MAX17048 fuel gauge, charging from the BQ25895 charger (I2C bus 1)
  POST /api/time              {"epoch": seconds}  set the system clock (and the CM5's RTC)
  POST /api/timezone          {"zone": "Europe/Paris"}
  GET  /api/usb               the USB stick and the files in its WEB-1 folder
  GET  /api/usb/file?name=    read a file from the stick        PUT /api/usb/file?name=   write one (the request body)
  POST /api/usb/eject         flush and unmount the stick
  POST /api/input             {"source": "mic" | "line"}  switch the WM8960's input (amixer commands below)
  GET  /api/update            how many new versions are on GitHub    POST /api/update   install them (git pull)
  POST /api/shutdown          save, then power off                   POST /api/saved    the page has saved
  GET  /api/events            server-sent events: "shutdown" (save now), "usb" (a stick came or went)

Standard library only. Run:  python3 web1-helper.py [--root ~/web1] [--port 8000] [--dev]
--dev is for trying it on a computer: no root commands and no power-off, a folder stands in for the USB stick
(WEB1_USB_DIR, default /tmp/web1-usb), WEB1_FAKE_BATTERY=1 reports a pretend battery, and POST /api/test/shutdown
runs the save-before-power-off steps without turning anything off.
"""
import argparse, ctypes, fcntl, json, os, queue, re, shutil, subprocess, sys, threading, time, urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

VERSION = '1.0'

# ---- settings for the WEB-1 board ----
I2C_BUS = 1                 # dtparam=i2c_arm=on
FUEL_GAUGE = 0x36           # MAX17048: VCELL 0x02, SOC 0x04
CHARGER = 0x6A              # BQ25895: REG0B status
USB_FOLDER = 'WEB-1'        # the folder WEB-1 uses on a USB stick
SOUNDCARD = 'wm8960soundcard'
# Which WM8960 input records: the built-in mic is on LINPUT1, the line-in jack on LINPUT3 / RINPUT3.
# The names are the codec driver's simple mixer controls; list yours with `amixer -c wm8960soundcard scontrols`.
INPUT_CMDS = {
    'mic':  [['Left Boost Mixer LINPUT1', 'on'], ['Right Boost Mixer RINPUT1', 'on'],
             ['Left Input Boost Mixer LINPUT3', '0'], ['Right Input Boost Mixer RINPUT3', '0'],
             ['Left Input Mixer Boost', 'on'], ['Right Input Mixer Boost', 'on']],
    'line': [['Left Boost Mixer LINPUT1', 'off'], ['Right Boost Mixer RINPUT1', 'off'],
             ['Left Input Boost Mixer LINPUT3', '5'], ['Right Input Boost Mixer RINPUT3', '5'],
             ['Left Input Mixer Boost', 'on'], ['Right Input Mixer Boost', 'on']],
}
# Optional: the ON/OFF switch as a signal. Today the switch cuts the power directly, so nothing can save at that moment.
# If the switch is wired to a GPIO (and the CM5 holds the power on until it has shut down), set it here,
# for example POWER_GPIO = ('gpiochip0', 26, 0): chip, line, and the value read when the switch is OFF.
POWER_GPIO = None

ARGS = None
ROOT = '.'
DEV = False
SAVED = threading.Event()
CLIENTS = []
CLIENTS_LOCK = threading.Lock()


def log(*a):
    print('[web1-helper]', *a, flush=True)


def run(cmd, timeout=20):
    """Run a command; return (ok, output). In --dev, root commands are only printed."""
    if DEV and cmd and cmd[0] in ('sudo', 'systemctl', 'amixer', 'udisksctl', 'umount', 'mount', 'date', 'timedatectl', 'hwclock'):
        log('dev, not running:', ' '.join(cmd))
        return True, ''
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode == 0, (p.stdout + p.stderr).strip()
    except Exception as e:
        return False, str(e)


# ---- I2C: one register read with a repeated start (I2C_RDWR) ----
class _Msg(ctypes.Structure):
    _fields_ = [('addr', ctypes.c_uint16), ('flags', ctypes.c_uint16), ('len', ctypes.c_uint16), ('buf', ctypes.POINTER(ctypes.c_uint8))]


class _Rdwr(ctypes.Structure):
    _fields_ = [('msgs', ctypes.POINTER(_Msg)), ('nmsgs', ctypes.c_uint32)]


def i2c_read(addr, reg, n):
    with open('/dev/i2c-%d' % I2C_BUS, 'rb+', buffering=0) as f:
        w = (ctypes.c_uint8 * 1)(reg)
        r = (ctypes.c_uint8 * n)()
        P = ctypes.POINTER(ctypes.c_uint8)
        msgs = (_Msg * 2)(_Msg(addr, 0, 1, ctypes.cast(w, P)), _Msg(addr, 1, n, ctypes.cast(r, P)))
        fcntl.ioctl(f.fileno(), 0x0707, _Rdwr(msgs, 2))
        return bytes(r)


def power():
    if DEV and os.environ.get('WEB1_FAKE_BATTERY'):
        t = time.time() / 60
        return {'ok': True, 'soc': round(60 + 30 * abs(((t / 10) % 2) - 1), 1), 'volts': 3.92, 'charging': int(t) % 4 == 0, 'plugged': int(t) % 4 == 0}
    try:
        v, s = i2c_read(FUEL_GAUGE, 0x02, 2), i2c_read(FUEL_GAUGE, 0x04, 2)
    except Exception as e:
        return {'ok': False, 'reason': 'no fuel gauge (%s)' % e.__class__.__name__}
    out = {'ok': True, 'volts': round(((v[0] << 8) | v[1]) * 78.125e-6, 3), 'soc': round(min(100.0, s[0] + s[1] / 256), 1), 'charging': False, 'plugged': False}
    try:
        st = i2c_read(CHARGER, 0x0B, 1)[0]
        vbus, chrg, pg = (st >> 5) & 7, (st >> 3) & 3, (st >> 2) & 1
        out['plugged'] = bool(pg) and vbus not in (0, 7)   # 7 = boost (running on the battery)
        out['charging'] = chrg in (1, 2)                     # pre-charge or fast charge
    except Exception:
        pass
    return out


# ---- USB stick ----
USB_MNT = '/mnt/web1-usb'   # where the helper mounts a stick itself
NO_MOUNT = set()            # partitions that would not mount (no file system, unknown format): not tried again


def disk_label(dev):
    try:
        for n in os.listdir('/dev/disk/by-label'):
            if os.path.realpath('/dev/disk/by-label/' + n) == dev:
                return n.replace('\\x20', ' ')
    except Exception:
        pass
    return 'USB STICK'


def usb_drive():
    if DEV:
        d = os.environ.get('WEB1_USB_DIR', '/tmp/web1-usb')
        os.makedirs(d, exist_ok=True)
        return {'label': 'TEST STICK', 'path': d, 'dev': None}
    def mounted():
        try:
            for line in open('/proc/mounts'):
                dev, mnt = line.split()[:2]
                if dev.startswith('/dev/sd') and (mnt.startswith('/media/') or mnt.startswith('/mnt/')):
                    mnt = mnt.replace('\\040', ' ')
                    if not os.path.exists(dev):  # pulled out without EJECT: let the old mount go
                        run(['sudo', '-n', 'umount', '-l', mnt])
                        continue
                    label = disk_label(dev) if mnt == USB_MNT else os.path.basename(mnt)
                    return {'label': label.upper()[:24], 'path': mnt, 'dev': dev}
        except Exception:
            pass
        return None
    d = mounted()
    if d:
        return d
    # plugged in but not mounted yet (kiosk mode has no desktop automounter): mount it with udisks, or with sudo
    try:
        seen = set()
        for blk in sorted(os.listdir('/sys/block')):
            if not blk.startswith('sd'):
                continue
            parts = sorted(p for p in os.listdir('/sys/block/' + blk) if p.startswith(blk)) or [blk]
            for p in parts:
                try:
                    size = open('/sys/class/block/%s/size' % p).read().strip()
                except Exception:
                    size = '?'
                key = p + ':' + size
                seen.add(key)
                if key in NO_MOUNT:
                    continue
                dev = '/dev/' + p
                ok = run(['udisksctl', 'mount', '-b', dev, '--no-user-interaction'])[0]
                if not ok and run(['sudo', '-n', 'mkdir', '-p', USB_MNT])[0]:
                    # FAT and exFAT sticks: mount them as this user, so WEB-1 can write to them
                    ok = (run(['sudo', '-n', 'mount', '-o', 'uid=%d,gid=%d' % (os.getuid(), os.getgid()), dev, USB_MNT])[0]
                          or run(['sudo', '-n', 'mount', dev, USB_MNT])[0])
                if ok:
                    return mounted()
                NO_MOUNT.add(key)
        NO_MOUNT.intersection_update(seen)
    except Exception:
        pass
    return None


def usb_folder(d):
    f = os.path.join(d['path'], USB_FOLDER)
    os.makedirs(f, exist_ok=True)
    return f


def safe_name(n):
    n = os.path.basename(n or '').strip()
    return n if n and not n.startswith('.') and re.fullmatch(r"[\w .()+,'&-]{1,120}", n) else None


def usb_listing():
    d = usb_drive()
    if not d:
        return {'ok': True, 'drive': None, 'files': []}
    f = usb_folder(d)
    try:
        st = shutil.disk_usage(d['path'])
        free = st.free
    except Exception:
        free = 0
    files = []
    for n in sorted(os.listdir(f), key=str.lower):
        p = os.path.join(f, n)
        if os.path.isfile(p) and not n.startswith('.'):
            files.append({'name': n, 'size': os.path.getsize(p)})
    return {'ok': True, 'drive': {'label': d['label'], 'free': free}, 'files': files}


# ---- events to the page ----
def broadcast(event, data):
    msg = ('event: %s\ndata: %s\n\n' % (event, json.dumps(data))).encode()
    with CLIENTS_LOCK:
        for q in CLIENTS:
            q.put(msg)


def watch_usb():
    last = None
    while True:
        d = usb_drive() if not DEV else {'path': os.environ.get('WEB1_USB_DIR', '/tmp/web1-usb')}
        key = d and d['path']
        if key != last:
            last = key
            broadcast('usb', {'present': bool(d)})
        time.sleep(2)


def begin_shutdown(reason):
    """Ask the page to save (it posts /api/saved when done), wait a few seconds at most, then power off."""
    log('power off requested:', reason)
    SAVED.clear()
    with CLIENTS_LOCK:
        listening = len(CLIENTS)
    broadcast('shutdown', {'reason': reason})
    if listening:
        log('page saved' if SAVED.wait(8) else 'page did not answer, powering off anyway')
    if DEV or reason == 'test':
        log('dev: would power off now')
        return
    subprocess.run(['sync'])
    if not run(['systemctl', 'poweroff'])[0]:
        run(['sudo', '-n', 'systemctl', 'poweroff'])


def watch_power_switch():
    if not POWER_GPIO:
        return
    chip, line, off = POWER_GPIO
    # libgpiod 2 (gpioget -c chip line) or 1 (gpioget chip line)
    cmds = [['gpioget', '-c', chip, str(line)], ['gpioget', chip, str(line)]]
    lows = 0
    while True:
        val = None
        for c in cmds:
            ok, o = run(c, timeout=3)
            m = re.search(r'(\d)\s*$', o) if ok else None
            if m:
                val = int(m.group(1))
                cmds = [c]
                break
        lows = lows + 1 if val == off else 0
        if lows >= 2:
            begin_shutdown('switch')
            return
        time.sleep(.25)


# ---- updates (the repository the helper runs from) ----
def git(*a, timeout=30):
    return run(['git', '-C', ROOT] + list(a), timeout=timeout)


def update_status():
    if not DEV:
        ok, o = git('fetch', '--quiet', 'origin', timeout=25)
        if not ok:
            return {'ok': False, 'reason': 'no connection'}
    ok1, cur = git('rev-parse', '--short', 'HEAD')
    ok2, lat = git('rev-parse', '--short', '@{u}')
    ok3, behind = git('rev-list', '--count', 'HEAD..@{u}')
    _, dirty = git('status', '--porcelain', '--untracked-files=no')
    if not (ok1 and ok2 and ok3):
        return {'ok': False, 'reason': 'not a git checkout'}
    return {'ok': True, 'current': cur, 'latest': lat, 'behind': int(behind or 0), 'dirty': bool(dirty)}


def update_install():
    if DEV:
        return {'ok': False, 'reason': 'dev mode: not updating'}
    ok, o = git('pull', '--ff-only', timeout=120)
    if ok:  # start again with the new helper once the answer is sent
        threading.Timer(1.0, lambda: os.execv(sys.executable, [sys.executable] + sys.argv)).start()
    return {'ok': ok, 'output': o[-400:]}


# ---- HTTP ----
class Handler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map, **{'.webmanifest': 'application/manifest+json', '.js': 'text/javascript', '.glb': 'model/gltf-binary'})

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, fmt, *a):
        if ARGS.verbose:
            super().log_message(fmt, *a)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def local_origin(self):
        o = self.headers.get('Origin') or ''
        return not o or re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', o)

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self, limit=1 << 30):
        n = int(self.headers.get('Content-Length') or 0)
        if n > limit:
            raise ValueError('too big')
        return self.rfile.read(n) if n else b''

    def translate_path(self, path):
        if urllib.parse.urlparse(path).path == '/hw.html' and not os.path.exists(os.path.join(ROOT, 'hw.html')):
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hw.html')
        return super().translate_path(path)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        p = u.path
        if not p.startswith('/api/'):
            return super().do_GET()
        try:
            if p == '/api/ping':
                return self.send_json({'ok': True, 'helper': VERSION, 'dev': DEV})
            if p == '/api/power':
                return self.send_json(power())
            if p == '/api/usb':
                return self.send_json(usb_listing())
            if p == '/api/usb/file':
                d, n = usb_drive(), safe_name((q.get('name') or [''])[0])
                if not d or not n or not os.path.isfile(os.path.join(usb_folder(d), n)):
                    return self.send_json({'ok': False}, 404)
                fp = os.path.join(usb_folder(d), n)
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(os.path.getsize(fp)))
                self.end_headers()
                with open(fp, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
                return
            if p == '/api/update':
                return self.send_json(update_status())
            if p == '/api/events':
                return self.events()
            return self.send_json({'ok': False, 'reason': 'unknown'}, 404)
        except Exception as e:
            return self.send_json({'ok': False, 'reason': str(e)}, 500)

    def events(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        q = queue.Queue()
        with CLIENTS_LOCK:
            CLIENTS.append(q)
        try:
            self.wfile.write(b': hello\n\n')
            self.wfile.flush()
            while True:
                try:
                    msg = q.get(timeout=15)
                except queue.Empty:
                    msg = b': keep-alive\n\n'
                self.wfile.write(msg)
                self.wfile.flush()
        except Exception:
            pass
        finally:
            with CLIENTS_LOCK:
                CLIENTS.remove(q)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if not self.local_origin():
            return self.send_json({'ok': False, 'reason': 'forbidden'}, 403)
        try:
            data = json.loads(self.body(1 << 16) or b'{}')
            if p == '/api/time':
                ep = int(data.get('epoch', 0))
                if ep < 1.6e9:
                    return self.send_json({'ok': False, 'reason': 'bad time'}, 400)
                ok, o = run(['sudo', '-n', 'date', '-u', '-s', '@%d' % ep])
                if ok and os.path.exists('/dev/rtc0'):
                    run(['sudo', '-n', 'hwclock', '-w'])
                return self.send_json({'ok': ok, 'output': o})
            if p == '/api/timezone':
                z = str(data.get('zone', ''))
                if not re.fullmatch(r'[A-Za-z]+(/[A-Za-z_+-]+){1,2}', z) or (not DEV and not os.path.exists('/usr/share/zoneinfo/' + z)):
                    return self.send_json({'ok': False, 'reason': 'unknown zone'}, 400)
                ok, o = run(['sudo', '-n', 'timedatectl', 'set-timezone', z])
                return self.send_json({'ok': ok, 'output': o})
            if p == '/api/input':
                src = data.get('source')
                if src not in INPUT_CMDS:
                    return self.send_json({'ok': False}, 400)
                res = [run(['amixer', '-c', SOUNDCARD, 'sset', c, v])[0] for c, v in INPUT_CMDS[src]]
                return self.send_json({'ok': all(res), 'source': src})
            if p == '/api/usb/eject':
                d = usb_drive()
                subprocess.run(['sync'])
                ok = True
                if d and d.get('dev'):
                    ok = run(['udisksctl', 'unmount', '-b', d['dev'], '--no-user-interaction'])[0] or run(['sudo', '-n', 'umount', d['path']])[0]
                return self.send_json({'ok': ok})
            if p == '/api/update':
                return self.send_json(update_install())
            if p == '/api/shutdown':
                threading.Thread(target=begin_shutdown, args=('menu',), daemon=True).start()
                return self.send_json({'ok': True})
            if p == '/api/saved':
                SAVED.set()
                return self.send_json({'ok': True})
            if p == '/api/test/shutdown' and DEV:
                threading.Thread(target=begin_shutdown, args=('test',), daemon=True).start()
                return self.send_json({'ok': True})
            return self.send_json({'ok': False, 'reason': 'unknown'}, 404)
        except Exception as e:
            return self.send_json({'ok': False, 'reason': str(e)}, 500)

    def do_PUT(self):
        u = urllib.parse.urlparse(self.path)
        if u.path != '/api/usb/file' or not self.local_origin():
            return self.send_json({'ok': False}, 404)
        d, n = usb_drive(), safe_name((urllib.parse.parse_qs(u.query).get('name') or [''])[0])
        if not d or not n:
            return self.send_json({'ok': False, 'reason': 'no stick' if not d else 'bad name'}, 400)
        try:
            data = self.body()
            fp = os.path.join(usb_folder(d), n)
            tmp = fp + '.part'
            with open(tmp, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, fp)
            return self.send_json({'ok': True, 'size': len(data)})
        except Exception as e:
            return self.send_json({'ok': False, 'reason': str(e)}, 500)


def main():
    global ARGS, ROOT, DEV
    ap = argparse.ArgumentParser(description='WEB-1 helper')
    ap.add_argument('--root', default=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')), help='the WEB-1 folder (the git checkout)')
    ap.add_argument('--port', type=int, default=8000)
    ap.add_argument('--dev', action='store_true', help='try it on a computer: no root commands, a folder as the USB stick')
    ap.add_argument('--verbose', action='store_true')
    ARGS = ap.parse_args()
    ROOT, DEV = os.path.abspath(os.path.expanduser(ARGS.root)), ARGS.dev
    threading.Thread(target=watch_usb, daemon=True).start()
    threading.Thread(target=watch_power_switch, daemon=True).start()
    srv = ThreadingHTTPServer(('127.0.0.1', ARGS.port), Handler)
    srv.daemon_threads = True
    log('WEB-1 helper %s serving %s on http://localhost:%d%s' % (VERSION, ROOT, ARGS.port, ' (dev)' if DEV else ''))
    srv.serve_forever()


if __name__ == '__main__':
    main()
