"""Block Studio — move single-block weights, press Generate, see the image (local tool, no LLM in the loop).

    python experiments/block_studio/block_studio.py          # opens http://127.0.0.1:8199
    python experiments/block_studio/block_studio.py --check  # 2 renders: must equal the bench files pixel for pixel

Needs ComfyUI running at http://127.0.0.1:8188 with the Arthemy Krea2 Tuner, exactly as for the
benches. Standard library only. Nothing in ComfyUI is changed: this script talks to ComfyUI's own
HTTP API from Python (so the browser never needs cross-origin access), and reads reference images
straight from the Text2Img folder.

* Generation uses the bench workflow (experiments/blk23_colorful.py: UNETLoader, ResetPatcher,
  Model Tuner in Real Value with a 34-slot vectors_override, euler_ancestral, 9 steps, cfg 1.0,
  1024x1280). A render made here with a bench's vector and seed is the same image as the bench's.
* Outputs: Text2Img/block_studio/<char>_<vectorhash>_seed<seed>_00001_.png, and one line per
  generation in Text2Img/block_studio/log.csv (time, character, seed, vector, file). Scratch, not a bench.
* References: the portrait atlas (benchmark_portraits/renders: four characters x two seeds x every
  block in both directions at the v4 doses) and phase C (benchmark_portraits/phase_c: base and the
  comics preset at four seeds, seven characters).
"""
from __future__ import annotations

import csv, hashlib, json, os, sys, threading, time, urllib.parse, urllib.request, uuid, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parent
sys.path.insert(0, str(EXP))
import blk23_colorful as c47                     # noqa: E402  the bench workflow
import portraits as P                            # noqa: E402  characters, seeds, prompt template

PORT = int(os.environ.get("BLOCK_STUDIO_PORT", "8199"))
COMFY = os.environ.get("COMFY_URL", c47.COMFY)
IMG_ROOT = Path(os.environ.get("BLOCK_STUDIO_IMG_ROOT", str(P.IMG_ROOT)))
OUT_SUB = "block_studio"
DATA = REPO / "data"
CLIENT_ID = uuid.uuid4().hex
LOG_LOCK = threading.Lock()

BANDS = [("Base", range(0, 2)), ("Style", range(2, 19)), ("Details", range(19, 23)), ("Correction", range(23, 28))]
TEXT_SLOTS = ["txtfusion layerwise 0", "txtfusion layerwise 1", "txtfusion refiner 0", "txtfusion refiner 1",
              "txtfusion projector", "txtmlp"]


def guide() -> dict:
    """Alessandro's by-eye guide (results/21-block-map.md): block -> (doses, negative, positive)."""
    out = {}
    for line in (REPO / "results" / "21-block-map.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0].isdigit() and len(cells[0]) == 2:
            out[int(cells[0])] = {"doses": cells[1], "neg": cells[2], "pos": cells[3]}
    return out


def characters() -> list:
    chars = [{"id": k, "name": k.split("_", 1)[1].replace("_", " "), "group": "calibration (block references)",
              "prompt": P.text(v)} for k, v in P.CALIBRATION.items()]
    chars += [{"id": k, "name": k.split("_", 1)[1].replace("_", " "), "group": "held out (no block references)",
               "prompt": P.text(v)} for k, v in P.HELD_OUT.items()]
    return chars


def references() -> dict:
    """{char: {seed: {"baseline": path, "preset": path, "blocks": {"<b><sign>": {"path", "dose"}}}}} for files on disk."""
    refs: dict = {}
    def put(char, seed, key, rel, dose=None, block=None):
        if not (IMG_ROOT / rel).exists():
            return
        d = refs.setdefault(char, {}).setdefault(seed, {"blocks": {}})
        if block is None:
            d[key] = rel
        else:
            d["blocks"][key] = {"path": rel, "dose": dose}
    for r in csv.DictReader(open(DATA / "portraits_atlas_plan.csv", encoding="utf-8")):
        rel = f"benchmark_portraits/renders/{r['expected_filename']}"
        if r["cond"] == "baseline":
            put(r["char"], r["seed"], "baseline", rel)
        elif r["block"] != "":
            sign = "-" if r["sign"] == "neg" else "+"
            put(r["char"], r["seed"], f"{int(r['block'])}{sign}", rel, dose=float(r["dose"]), block=int(r["block"]))
    for r in csv.DictReader(open(DATA / "portraits_preset_plan.csv", encoding="utf-8")):
        if r["set"] in ("calibration", "held_out"):
            put(r["char"], r["seed"], r["cond"], f"benchmark_portraits/phase_c/{r['expected_filename']}")
    return refs


def presets() -> list:
    out = [{"name": "zero (no edit)", "vector": [0.0] * 34}]
    for f in sorted((REPO / "presets").glob("*.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            v = j.get("vectors_override")
            if isinstance(v, list) and len(v) == 34:
                out.append({"name": j.get("name", f.stem), "vector": [float(x) for x in v], "description": j.get("description", "")})
        except Exception:
            pass
    return out


def comfy(path: str, payload: dict | None = None):
    req = urllib.request.Request(COMFY + path, data=None if payload is None else json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read() or b"{}")


def generate(char: str, seed: int, vector: list) -> dict:
    ch = next(c for c in characters() if c["id"] == char)
    vec = [round(float(x), 4) for x in vector][:34] + [0.0] * max(0, 34 - len(vector))
    vstr = ",".join(f"{x:.4f}" for x in vec) if any(vec) else ""
    tag = hashlib.sha1((vstr or "zero").encode()).hexdigest()[:8]
    prefix = f"{char}_{tag}_seed{seed}"
    row = {"vectors_override": vstr, "prompt_text": ch["prompt"], "seed": str(seed), "output_prefix": prefix,
           **P.SETTINGS}
    wf = c47.workflow(row)
    wf["61"]["inputs"]["filename_prefix"] = f"{OUT_SUB}/{prefix}"
    res = comfy("/prompt", {"prompt": wf, "client_id": CLIENT_ID})
    if "prompt_id" not in res:
        raise RuntimeError(json.dumps(res)[:500])
    return {"prompt_id": res["prompt_id"], "vector": vec, "prefix": prefix}


def status(prompt_id: str, meta: dict) -> dict:
    h = comfy(f"/history/{prompt_id}")
    if prompt_id not in h:
        q = comfy("/queue")
        pos = [i for i, x in enumerate(q.get("queue_pending", [])) if x[1] == prompt_id]
        return {"state": "queued" if pos else "running", "ahead": pos[0] if pos else 0}
    entry = h[prompt_id]
    st = entry.get("status", {})
    if st.get("status_str") == "error":
        msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
        return {"state": "error", "error": (msgs[0][1].get("exception_message") if msgs else "ComfyUI reported an error")}
    for node_out in entry.get("outputs", {}).values():
        for im in node_out.get("images", []):
            rel = f"{im.get('subfolder', '')}/{im['filename']}".lstrip("/")
            log(meta, rel)
            return {"state": "done", "path": rel}
    return {"state": "running", "ahead": 0}


def log(meta: dict, rel: str) -> None:
    if meta.get("_logged"):
        return
    meta["_logged"] = True
    f = IMG_ROOT / OUT_SUB / "log.csv"
    with LOG_LOCK:
        f.parent.mkdir(parents=True, exist_ok=True)
        new = not f.exists()
        with open(f, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["time", "character", "seed", "vectors_override", "file"])
            w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), meta["char"], meta["seed"],
                        ",".join(f"{x:.4f}" for x in meta["vector"]), rel])


JOBS: dict = {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/config":
                g = guide()
                blocks = [{"index": b, "band": band, **g.get(b, {})} for band, rng in BANDS for b in rng]
                return self.send(200, {"characters": characters(), "refs": references(), "presets": presets(),
                                       "blocks": blocks, "text_slots": TEXT_SLOTS,
                                       "seeds": {"atlas (block references)": P.SEEDS_A, "phase C (base and preset)": P.SEEDS_C}})
            if u.path == "/api/status":
                pid = q["id"][0]
                return self.send(200, status(pid, JOBS.get(pid, {})))
            if u.path == "/api/ping":
                try:
                    comfy("/system_stats")
                    return self.send(200, {"comfy": True})
                except Exception as e:
                    return self.send(200, {"comfy": False, "error": str(e)})
            if u.path == "/img":
                rel = q["path"][0]
                f = (IMG_ROOT / rel).resolve()
                if IMG_ROOT.resolve() not in f.parents or not f.is_file():
                    return self.send(404, {"error": "not found"})
                return self.send(200, f.read_bytes(), "image/png")
            return self.send(404, {"error": "not found"})
        except Exception as e:
            return self.send(500, {"error": str(e)})

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/generate":
                r = generate(body["char"], int(body["seed"]), body["vector"])
                JOBS[r["prompt_id"]] = {"char": body["char"], "seed": int(body["seed"]), "vector": r["vector"]}
                return self.send(200, r)
            return self.send(404, {"error": "not found"})
        except Exception as e:
            return self.send(500, {"error": str(e)})


def check() -> int:
    """Two renders through the studio's own path, compared with the bench files pixel for pixel:
    the dwarf at seed 2236067 with no edit (atlas baseline) and with blk09 +0.55 (atlas reference)."""
    import numpy as np
    from PIL import Image
    refs = references()["D1_dwarf_paladin"]["2236067"]
    cases = [("no edit", [0.0] * 34, refs["baseline"])]
    v = [0.0] * 34; v[9] = 0.55
    cases.append(("blk09 +0.55", v, refs["blocks"]["9+"]["path"]))
    ok = True
    for name, vec, ref in cases:
        r = generate("D1_dwarf_paladin", 2236067, vec)
        meta = {"char": "D1_dwarf_paladin", "seed": 2236067, "vector": r["vector"]}
        for _ in range(600):
            s = status(r["prompt_id"], meta)
            if s["state"] in ("done", "error"):
                break
            time.sleep(1)
        if s["state"] != "done":
            print(f"{name}: {s}"); ok = False; continue
        a = np.asarray(Image.open(IMG_ROOT / s["path"]).convert("RGB"), dtype=np.int16)
        b = np.asarray(Image.open(IMG_ROOT / ref).convert("RGB"), dtype=np.int16)
        d = int(np.abs(a - b).max()) if a.shape == b.shape else -1
        print(f"{name}: max abs diff against {ref} = {d}")
        ok &= d == 0
    print("CHECK", "PASS - the studio reproduces the bench" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--check" in sys.argv:
        raise SystemExit(check())
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Block Studio at {url}  (ComfyUI: {COMFY}, images: {IMG_ROOT})")
    if os.environ.get("BLOCK_STUDIO_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
