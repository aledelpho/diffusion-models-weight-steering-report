#!/usr/bin/env python3
"""Independent provenance check on the two new benches, read from the renders' own metadata.

Checked against the plan files, row by row, without trusting the queueing scripts:
  - the tuner drive matches the mechanism the bench requires, and only that mechanism;
  - BASELINE ROWS HAVE NO TUNER NODE AT ALL. A tuner set to zero is not the same thing as no
    tuner, and the comparison with the existing corpus depends on which one was used;
  - seed, sampler, scheduler, steps, CFG, size and prompt text match the plan.

Bench 1 (leaf): named group input Block_4 = -0.2, vectors_override empty, granular_json empty.
Bench 2 (blk16): 34-slot vectors_override, slot 16 only, every named group input 0.0.

Writes data/provenance_leaf_collapse.csv and data/provenance_blk16_ladder.csv. No render.
"""
import csv, json, os
from PIL import Image

H = os.path.expanduser("~/mnt")
LEAF = f"{H}/benchmark_leaf_collapse/renders"
BLK = f"{H}/benchmark_blk16_ladder/renders"
NAMED = ["Text_Fusion", "Time_Embed", "Projection",
         "Block_1", "Block_2", "Block_3", "Block_4", "Block_5", "Block_6"]


def wf(path):
    return json.loads(Image.open(path).info["prompt"])


def tuner(w):
    n = [v for v in w.values() if v.get("class_type") == "ArthemyKrea2ModelTuner"]
    return n[0]["inputs"] if n else None


def sampler(w):
    n = [v for v in w.values() if v.get("class_type") == "KSampler"]
    return n[0]["inputs"] if n else None


def texts(w):
    return [v["inputs"].get("text", "") for v in w.values()
            if v.get("class_type") == "CLIPTextEncode" and isinstance(v["inputs"].get("text"), str)]


def common(row, w, problems):
    s = sampler(w)
    if s is None:
        problems.append("no KSampler"); return
    if int(s.get("seed", -1)) != int(row["seed"]):
        problems.append(f"seed {s.get('seed')} != {row['seed']}")
    for k, col, cast in (("steps", "steps", int), ("cfg", "cfg", float),
                         ("sampler_name", "sampler", str), ("scheduler", "scheduler", str)):
        if cast(s.get(k)) != cast(row[col]):
            problems.append(f"{k} {s.get(k)} != {row[col]}")
    if row["prompt_text"] not in texts(w):
        problems.append("prompt text not found in workflow")


def check_leaf():
    plan = list(csv.DictReader(open("data/leaf_collapse_plan.csv", encoding="utf-8")))
    out = []
    for row in plan:
        f = f"{LEAF}/{row['expected_filename']}"
        p = []
        if not os.path.exists(f):
            p.append("MISSING FILE")
        else:
            w = wf(f)
            common(row, w, p)
            t = tuner(w)
            if row["treatment"] == "none":
                if t is not None:
                    p.append("BASELINE HAS A TUNER NODE"
                             + (" (all zero)" if all(float(t.get(k, 0)) == 0 for k in NAMED)
                                else " (non-zero!)"))
            else:
                if t is None:
                    p.append("PERTURBED ROW HAS NO TUNER")
                else:
                    if t.get("mode") != "Real Value":
                        p.append(f"mode {t.get('mode')}")
                    if t.get("vectors_override", "") != "":
                        p.append("vectors_override NOT empty -- wrong mechanism")
                    if t.get("granular_json", "") != "":
                        p.append("granular_json not empty")
                    for k in NAMED:
                        want = -0.2 if k == "Block_4" else 0.0
                        if abs(float(t.get(k, 0.0)) - want) > 1e-9:
                            p.append(f"{k}={t.get(k)} want {want}")
        out.append(dict(file=row["expected_filename"], arm=row["arm"],
                        prompt_id=row["prompt_id"], seed=row["seed"],
                        treatment=row["treatment"], ok=int(not p), problems="; ".join(p)))
    return out, "data/provenance_leaf_collapse.csv"


def check_blk():
    plan = list(csv.DictReader(open("data/blk16_ladder_plan.csv", encoding="utf-8")))
    out = []
    for row in plan:
        f = f"{BLK}/{row['expected_filename']}"
        p = []
        if not os.path.exists(f):
            p.append("MISSING FILE")
        else:
            w = wf(f)
            common(row, w, p)
            t = tuner(w)
            if t is None:
                p.append("NO TUNER")
            else:
                if t.get("mode") != "Real Value":
                    p.append(f"mode {t.get('mode')}")
                if t.get("granular_json", "") != "":
                    p.append("granular_json not empty")
                got = [float(x) for x in t.get("vectors_override", "").split(",") if x.strip()]
                want = [float(x) for x in row["vectors_override"].split(",")]
                if len(got) != 34:
                    p.append(f"{len(got)} slots, want 34")
                elif any(abs(a - b) > 1e-9 for a, b in zip(got, want)):
                    p.append("vector differs from plan: "
                             + ";".join(f"{i}={a:+.3f} want {b:+.3f}"
                                        for i, (a, b) in enumerate(zip(got, want)) if abs(a-b) > 1e-9))
                for k in NAMED:
                    if abs(float(t.get(k, 0.0))) > 1e-9:
                        p.append(f"named input {k}={t.get(k)} should be 0")
        out.append(dict(file=row["expected_filename"], condition=row["condition"],
                        prompt_id=row["prompt_id"], seed=row["seed"], dose=row["dose"],
                        arm=row["arm"], ok=int(not p), problems="; ".join(p)))
    return out, "data/provenance_blk16_ladder.csv"


def main():
    for rows, path in (check_leaf(), check_blk()):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
            for r in rows: w.writerow(r)
        k = sum(r["ok"] for r in rows)
        print(f"{path}: {k}/{len(rows)} clean")
        for r in rows:
            if not r["ok"]:
                print(f"    {r['file']}: {r['problems']}")


if __name__ == "__main__":
    main()
