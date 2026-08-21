import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

URL = os.environ["TRUENAS_URL"].rstrip("/")
KEY = os.environ["TRUENAS_API_KEY"]
PREFIXES = [p for p in os.environ.get("DATASET_PREFIXES", "").split(",") if p]
INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "60"))
TIMEOUT = int(os.environ.get("SCRAPE_TIMEOUT", "30"))
PORT = int(os.environ.get("PORT", "9812"))

GAUGES = [
    ("volsize", "truenas_zvol_volsize_bytes", "Configured size of the zvol"),
    ("used", "truenas_zvol_used_bytes", "Total space charged to the zvol"),
    ("usedbydataset", "truenas_zvol_usedbydataset_bytes", "Space used by live data"),
    ("usedbysnapshots", "truenas_zvol_usedbysnapshots_bytes", "Space held by snapshots"),
    ("usedbyrefreservation", "truenas_zvol_usedbyrefreservation_bytes", "Space held by the refreservation"),
    ("refreservation", "truenas_zvol_refreservation_bytes", "Configured refreservation"),
    ("available", "truenas_zvol_available_bytes", "Space the zvol could still grow into"),
    ("volblocksize", "truenas_zvol_volblocksize_bytes", "Volume block size"),
    ("compressratio", "truenas_zvol_compressratio", "Compression ratio achieved"),
]

lock = threading.Lock()
payload = ""


def flatten(nodes):
    seen = {}
    stack = list(nodes)
    while stack:
        node = stack.pop()
        name = node.get("name")
        if name and name not in seen:
            seen[name] = node
            stack.extend(node.get("children") or [])
    return list(seen.values())


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
    request = urllib.request.Request(
        URL + "/api/v2.0/pool/dataset",
        headers={"Authorization": "Bearer " + KEY},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.load(response)


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
            zvols = [
                dataset
                for dataset in flatten(fetch())
                if dataset.get("type") == "VOLUME"
                and (not PREFIXES or any(dataset["name"].startswith(p) for p in PREFIXES))
            ]
            rendered = render(zvols, time.time() - started, True)
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
