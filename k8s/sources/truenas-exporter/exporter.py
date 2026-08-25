import base64
import json
import os
import socket
import ssl
import struct
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

URL = os.environ.get("TRUENAS_URL", "wss://truenas.mchill.lan/api/current")
KEY = os.environ["TRUENAS_API_KEY"]
PREFIXES = [p for p in os.environ.get("DATASET_PREFIXES", "").split(",") if p]
INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "60"))
TIMEOUT = int(os.environ.get("SCRAPE_TIMEOUT", "30"))
VERIFY = os.environ.get("TRUENAS_TLS_VERIFY", "false").lower() == "true"
PORT = int(os.environ.get("PORT", "9812"))

PROPERTIES = [
    "volsize", "used", "usedbydataset", "usedbysnapshots", "usedbyrefreservation",
    "refreservation", "referenced", "logicalreferenced", "logicalused", "written",
    "available", "volblocksize", "compressratio",
]

GAUGES = [
    ("volsize", "truenas_zvol_volsize_bytes", "Configured size of the zvol"),
    ("used", "truenas_zvol_used_bytes", "Total space charged to the zvol"),
    ("usedbydataset", "truenas_zvol_usedbydataset_bytes", "Space used by live data"),
    ("usedbysnapshots", "truenas_zvol_usedbysnapshots_bytes", "Space held by snapshots"),
    ("usedbyrefreservation", "truenas_zvol_usedbyrefreservation_bytes", "Space held by the refreservation"),
    ("refreservation", "truenas_zvol_refreservation_bytes", "Configured refreservation"),
    ("referenced", "truenas_zvol_referenced_bytes", "Physical space referenced by the live zvol"),
    ("logicalreferenced", "truenas_zvol_logicalreferenced_bytes", "Logical space referenced before compression"),
    ("logicalused", "truenas_zvol_logicalused_bytes", "Logical space used including snapshots"),
    ("written", "truenas_zvol_written_bytes", "Space written since the previous snapshot"),
    ("available", "truenas_zvol_available_bytes", "Space the zvol could still grow into"),
    ("volblocksize", "truenas_zvol_volblocksize_bytes", "Volume block size"),
    ("compressratio", "truenas_zvol_compressratio", "Compression ratio achieved"),
]

lock = threading.Lock()
payload = ""


class Socket:
    def __init__(self, url, timeout, verify):
        parsed = urllib.parse.urlsplit(url)
        secure = parsed.scheme in ("wss", "https")
        port = parsed.port or (443 if secure else 80)
        if not secure:
            raise RuntimeError("refusing to send the API key over %s" % parsed.scheme)
        raw = socket.create_connection((parsed.hostname, port), timeout=timeout)
        if verify:
            context = ssl.create_default_context()
        else:
            context = ssl._create_unverified_context()
        self.sock = context.wrap_socket(raw, server_hostname=parsed.hostname)
        self.buffer = b""
        self.handshake(parsed.hostname, parsed.path or "/api/current")
        self.counter = 0

    def handshake(self, host, path):
        nonce = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((
            "GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
            "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n" % (path, host, nonce)).encode())
        while b"\r\n\r\n" not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("connection closed during handshake")
            self.buffer += chunk
        head, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
        status = head.split(b"\r\n")[0].decode()
        if "101" not in status:
            raise RuntimeError("websocket handshake failed: %s" % status)

    def take(self, count):
        while len(self.buffer) < count:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise RuntimeError("connection closed")
            self.buffer += chunk
        out, self.buffer = self.buffer[:count], self.buffer[count:]
        return out

    def read(self):
        body = b""
        while True:
            first, second = self.take(2)
            final, opcode = first & 0x80, first & 0x0F
            masked, length = second & 0x80, second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self.take(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self.take(8))[0]
            mask = self.take(4) if masked else None
            frame = self.take(length)
            if mask:
                frame = bytes(b ^ mask[i % 4] for i, b in enumerate(frame))
            if opcode == 0x8:
                raise RuntimeError("server closed the connection")
            if opcode in (0x9, 0xA):
                continue
            body += frame
            if final:
                return body

    def call(self, method, params):
        self.counter += 1
        text = json.dumps({"jsonrpc": "2.0", "id": self.counter,
                           "method": method, "params": params}).encode()
        header = b"\x81"
        size = len(text)
        if size < 126:
            header += struct.pack("!B", 0x80 | size)
        elif size < 65536:
            header += struct.pack("!BH", 0x80 | 126, size)
        else:
            header += struct.pack("!BQ", 0x80 | 127, size)
        mask = os.urandom(4)
        self.sock.sendall(header + mask +
                          bytes(b ^ mask[i % 4] for i, b in enumerate(text)))
        response = json.loads(self.read())
        if "error" in response:
            raise RuntimeError("%s: %s" % (method, response["error"]))
        return response["result"]

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def number(field):
    if not isinstance(field, dict):
        return None
    value = field.get("parsed")
    if value is None or isinstance(value, bool):
        value = field.get("rawvalue")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch():
    connection = Socket(URL, TIMEOUT, VERIFY)
    try:
        if connection.call("auth.login_with_api_key", [KEY]) is not True:
            raise RuntimeError("API key rejected")
        datasets = connection.call("pool.dataset.query", [
            [["type", "=", "VOLUME"]],
            {"extra": {"properties": PROPERTIES, "retrieve_children": False}},
        ])
    finally:
        connection.close()
    return [d for d in datasets
            if not PREFIXES or any(d["name"].startswith(p) for p in PREFIXES)]


def escape(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')


def fmt(value):
    if value.is_integer() and abs(value) < 2 ** 53:
        return "%d" % int(value)
    return repr(value)


def render(zvols, duration, ok):
    lines = []
    for prop, metric, description in GAUGES:
        rows = []
        for zvol in zvols:
            value = number(zvol.get(prop))
            if value is None:
                continue
            labels = 'dataset="%s",pool="%s",volume="%s"' % (
                escape(zvol["name"]),
                escape(zvol.get("pool") or ""),
                escape(zvol["name"].rsplit("/", 1)[-1]),
            )
            rows.append("%s{%s} %s" % (metric, labels, fmt(value)))
        if rows:
            lines.append("# HELP %s %s" % (metric, description))
            lines.append("# TYPE %s gauge" % metric)
            lines.extend(rows)
    lines.append("# HELP truenas_exporter_up Whether the last TrueNAS API scrape succeeded")
    lines.append("# TYPE truenas_exporter_up gauge")
    lines.append("truenas_exporter_up %d" % (1 if ok else 0))
    lines.append("# HELP truenas_exporter_scrape_duration_seconds Duration of the last TrueNAS API scrape")
    lines.append("# TYPE truenas_exporter_scrape_duration_seconds gauge")
    lines.append("truenas_exporter_scrape_duration_seconds %s" % repr(duration))
    lines.append("# HELP truenas_exporter_zvols Number of zvols reported")
    lines.append("# TYPE truenas_exporter_zvols gauge")
    lines.append("truenas_exporter_zvols %d" % len(zvols))
    return "\n".join(lines) + "\n"


def collect():
    global payload
    while True:
        started = time.time()
        try:
            rendered = render(fetch(), time.time() - started, True)
        except Exception as error:
            print("scrape failed: %s" % error, flush=True)
            rendered = render([], time.time() - started, False)
        with lock:
            payload = rendered
        time.sleep(INTERVAL)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] not in ("/", "/metrics"):
            self.send_error(404)
            return
        with lock:
            body = payload.encode()
        if not body:
            self.send_error(503, "no scrape completed yet")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    threading.Thread(target=collect, daemon=True).start()
    HTTPServer(("", PORT), Handler).serve_forever()
