# -*- coding: utf-8 -*-
"""
experiments/score_headlights.py

Impianto per lo scoring cieco dei fari sulle 280 immagini di Stage 9:
1. Modalita' --prepare:
   - Filtra le 280 immagini di stile da data/stage9_images.csv.
   - Calcola un hash a 12 caratteri per ciascuna immagine (SHA-256 salato).
   - Mescola l'ordine con seme fisso e registrato (seed = 20260918).
   - Copia le immagini in viewer/blind_headlights/<hash_id>.png rimuovendo metadati di testo.
   - Scrive data/stage9_headlights_key.csv (da NON aprire fino al completamento dello scoring).
2. Modalita' --serve:
   - Avvia un server web locale minimale sulla porta 8089.
   - Serve l'interfaccia interattiva viewer/headlights_annotator.html.
   - Gestisce l'endpoint POST /api/score per salvare incrementale data/stage9_headlights_raw.csv.
"""

import os
import sys
import csv
import json
import random
import hashlib
import shutil
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PIL import Image
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
DATA_DIR = os.path.join(REPORT_ROOT, "data")
VIEWER_DIR = os.path.join(REPORT_ROOT, "viewer")
BLIND_DIR = os.path.join(VIEWER_DIR, "blind_headlights")

MANIFEST_CSV = os.path.join(DATA_DIR, "stage9_images.csv")
KEY_CSV = os.path.join(DATA_DIR, "stage9_headlights_key.csv")
RAW_CSV = os.path.join(DATA_DIR, "stage9_headlights_raw.csv")
BBOX_RAW_CSV = os.path.join(DATA_DIR, "stage9_bbox_raw.csv")

SHUFFLE_SEED = 20260918
SALT = "arthemy_stage10_blind_headlights_salt_v1"


def prepare_blind_dataset():
    print(f"=== PREPARAZIONE SET CIECO STAGE 10 (LAVORO A) ===")
    if not os.path.exists(MANIFEST_CSV):
        raise SystemExit(f"Manifesto non trovato: {MANIFEST_CSV}")

    os.makedirs(BLIND_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(MANIFEST_CSV, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    # Filtra solo i prompt di stile (arm == 'style_variants')
    style_rows = [r for r in reader if r.get("arm") == "style_variants"]
    if len(style_rows) != 280:
        raise SystemExit(f"Attese 280 immagini di stile, trovate: {len(style_rows)}")

    print(f"[1/4] Trovate 280 immagini di stile in {MANIFEST_CSV}")

    # Creazione record con hash univoco salato
    records = []
    seen_hashes = set()
    for r in style_rows:
        root = r["renders_root"]
        rel = r["image_path"].replace("/", os.sep)
        src_path = os.path.join(root, os.path.basename(rel))
        if not os.path.exists(src_path):
            src_path = os.path.join(root, rel)
        if not os.path.exists(src_path):
            raise SystemExit(f"Immagine sorgente mancante: {src_path}")

        # Hash salato a 12 caratteri esadecimali
        h_payload = f"{SALT}_{r['prompt_sha1']}_{r['cond_name']}_{r['seed']}".encode("utf-8")
        hash_id = hashlib.sha256(h_payload).hexdigest()[:12]
        if hash_id in seen_hashes:
            raise SystemExit(f"Collisione hash imprevista su {hash_id}")
        seen_hashes.add(hash_id)

        records.append({
            "hash_id": hash_id,
            "src_path": src_path,
            "prompt_id": r["prompt_id"],
            "prompt_sha1": r["prompt_sha1"],
            "cond_name": r["cond_name"],
            "seed": r["seed"],
            "prompt_text": r.get("prompt_text", "")
        })

    # [2/4] Mescolamento con seme registrato
    rng = random.Random(SHUFFLE_SEED)
    rng.shuffle(records)
    print(f"[2/4] Ordine di presentazione rimescolato con seed deterministico: {SHUFFLE_SEED}")

    # [3/4] Copia e stripping metadati PNG verso viewer/blind_headlights/<hash_id>.png
    print(f"[3/4] Copia di 280 immagini in {BLIND_DIR}...")
    manifest_blind_list = []
    for idx, rec in enumerate(records, 1):
        dst_filename = f"{rec['hash_id']}.png"
        dst_path = os.path.join(BLIND_DIR, dst_filename)

        # Ricreiamo un'immagine pulita da metadati in memoria
        with Image.open(rec["src_path"]) as img:
            clean_img = Image.fromarray(np.array(img.convert("RGB")))
            clean_img.save(dst_path, "PNG")

        manifest_blind_list.append({
            "order": idx,
            "hash_id": rec["hash_id"],
            "filename": dst_filename
        })

    # Scrive l'elenco cieco per l'annotatore (solo ordine e hash_id, NESSUN metadato)
    blind_list_file = os.path.join(VIEWER_DIR, "blind_order.json")
    with open(blind_list_file, "w", encoding="utf-8") as f:
        json.dump(manifest_blind_list, f, indent=2)
    print(f"      Elenco cieco salvato in: {blind_list_file}")

    # [4/4] Scrittura della chiave segreta (DA NON APRIRE)
    with open(KEY_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["order", "hash_id", "prompt_id", "prompt_sha1", "cond_name", "seed", "src_path"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, rec in enumerate(records, 1):
            writer.writerow({
                "order": idx,
                "hash_id": rec["hash_id"],
                "prompt_id": rec["prompt_id"],
                "prompt_sha1": rec["prompt_sha1"],
                "cond_name": rec["cond_name"],
                "seed": rec["seed"],
                "src_path": os.path.basename(rec["src_path"])
            })

    print(f"[4/4] Chiave segreta salvata in: {KEY_CSV}")
    print("      >>> AVVISO METODOLOGICO: Non aprire la chiave prima che tutti i 280 punteggi siano registrati!")
    print("=== PREPARAZIONE COMPLETATA CON SUCCESSO ===")


class BlindScoringHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=REPORT_ROOT, **kwargs)

    def do_POST(self):
        if self.path == "/api/score":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            hash_id = data.get("hash_id")
            code = data.get("code")
            ts = data.get("timestamp_ms")

            # Salva riga su stage9_headlights_raw.csv
            file_exists = os.path.exists(RAW_CSV)
            with open(RAW_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["hash_id", "code", "timestamp_ms"])
                writer.writerow([hash_id, code, ts])

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        elif self.path == "/api/bbox":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            hash_id = data.get("hash_id")
            top = data.get("top", [0, 0])
            bottom = data.get("bottom", [0, 0])
            left = data.get("left", [0, 0])
            right = data.get("right", [0, 0])
            w = data.get("bbox_width", 0)
            h = data.get("bbox_height", 0)
            area_frac = data.get("bbox_area_frac", 0.0)
            ts = data.get("timestamp_ms")

            file_exists = os.path.exists(BBOX_RAW_CSV)
            with open(BBOX_RAW_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "hash_id", "top_x", "top_y", "bottom_x", "bottom_y",
                        "left_x", "left_y", "right_x", "right_y",
                        "bbox_width", "bbox_height", "bbox_area_frac", "timestamp_ms"
                    ])
                writer.writerow([
                    hash_id, top[0], top[1], bottom[0], bottom[1],
                    left[0], left[1], right[0], right[1],
                    w, h, area_frac, ts
                ])

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_server(port=8089):
    server = HTTPServer(("127.0.0.1", port), BlindScoringHandler)
    print(f"Server di scoring attivo su http://127.0.0.1:{port}/viewer/headlights_annotator.html")
    print("Premi Ctrl+C per arrestare il server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer arrestato.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Prepara le 280 immagini cieche e la chiave")
    parser.add_argument("--serve", action="store_true", help="Avvia il server di scoring per l'annotatore")
    parser.add_argument("--port", type=int, default=8089, help="Porta per il server")
    args = parser.parse_args()

    if args.prepare:
        prepare_blind_dataset()
    elif args.serve:
        run_server(args.port)
    else:
        parser.print_help()
