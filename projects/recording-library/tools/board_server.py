#!/usr/bin/env python3
"""Plansza filmów na localhost — pełne filmy z final/samples, decyzje i uwagi w data/board-state.json.

Mateusz 12.10: „wolę to mieć na localhost” (artefakt miał tylko 15-sekundowe podglądy). Ta sama
plansza co artefakt (sekcje, ocena, uwagi z czasem, plan pracy), ale wideo grają w pełnej jakości,
a stan zapisuje się do pliku w repo, więc da się go commitować i czytać z rozmowy z Claude.

  python3 tools/board_server.py            # http://localhost:8765
  python3 tools/board_server.py --lan      # też dla innych w tej samej sieci (agencja w biurze)

API (JSON): GET /api/board · POST /api/move {id, section} · POST /api/notes {video, at, type, text, author}
            POST /api/notes/<id> {done} · POST /api/plan {text}
"""
import argparse
import json
import mimetypes
import os
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from sources import BUILD, DATA, PROJECT

STATE = DATA / "board-state.json"
PAGE = PROJECT / "packaging" / "plansza-local.html"
SAMPLES = PROJECT / "final" / "samples"
THUMBS = BUILD / "board" / "thumbs"
LOCK = threading.Lock()


def load_state():
    return json.load(open(STATE)) if STATE.exists() else {"sections": {}, "notes": [], "plan": ""}


def save_state(state):
    tmp = STATE.with_suffix(".tmp")
    json.dump(state, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def board():
    rows = json.load(open(DATA / "scorecard.json"))["rows"]
    history = json.load(open(DATA / "video-history.json")) if (DATA / "video-history.json").exists() else {}
    state = load_state()
    for r in rows:
        r["section"] = state["sections"].get(r["id"], "ocena")
        r["history"] = history.get(r["id"], []) or history.get(r["clip"], [])
        r["video"] = f"/samples/{r['file']}"
        r["thumb"] = f"/thumbs/{r['id']}.jpg"
    return {"videos": rows, "notes": state["notes"], "plan": state["plan"]}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):   # cicho — w terminalu tylko zapisy
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        """Pliki wideo z obsługą Range — bez tego przeglądarka nie przewija długich odcinków."""
        if not path.is_file():
            return self.send_error(404)
        size = path.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if a and b else end
        self.send_response(206 if rng else 200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if rng:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        if path in ("/", "/index.html"):
            return self.send_file(PAGE)
        if path == "/api/board":
            return self.send_json(board())
        if path.startswith("/samples/"):
            return self.send_file(SAMPLES / os.path.basename(path))
        if path.startswith("/thumbs/"):
            return self.send_file(THUMBS / os.path.basename(path))
        self.send_error(404)

    def do_POST(self):
        path = unquote(self.path.split("?")[0])
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        with LOCK:
            state = load_state()
            if path == "/api/move":
                state["sections"][data["id"]] = data["section"]
                print(f"↦ {data['id']} → {data['section']}", flush=True)
            elif path == "/api/notes":
                note = {"id": uuid.uuid4().hex[:10], "video": data["video"], "at": data.get("at", ""), "type": data.get("type", ""),
                        "text": data["text"], "author": data.get("author", ""), "createdAt": int(time.time() * 1000), "done": False}
                state["notes"].append(note)
                print(f"✎ {note['video']} {note['at']} — {note['text']}", flush=True)
            elif path.startswith("/api/notes/"):
                for n in state["notes"]:
                    if n["id"] == path.rsplit("/", 1)[1]:
                        n["done"] = bool(data.get("done"))
            elif path == "/api/plan":
                state["plan"] = data.get("text", "")
            else:
                return self.send_error(404)
            save_state(state)
        self.send_json({"ok": True})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--lan", action="store_true", help="nasłuch na wszystkich interfejsach (inni w sieci)")
    a = ap.parse_args()
    host = "0.0.0.0" if a.lan else "127.0.0.1"
    print(f"Plansza filmów: http://localhost:{a.port}  (stan: {STATE.relative_to(PROJECT)})", flush=True)
    ThreadingHTTPServer((host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
