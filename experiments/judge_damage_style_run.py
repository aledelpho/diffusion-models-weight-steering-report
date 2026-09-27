#!/usr/bin/env python3
"""Damage or style? Two forced-choice arms on benchmark_mappa.

Pre-registration: docs/prereg_damage_or_style.md (2026-09-27), frozen before any call.
Runbook:          docs/RUNBOOK_2026-09-27_damage_or_style.md

Arm A -- damage:  baseline vs perturbed, same prompt and seed, both orders.
Arm B -- style :  a reference, and two candidates from a DIFFERENT prompt and seed; one carries
                  the same block/dose/sign, the other a different block MATCHED IN ||D|| at that
                  dose. Chance is 50%. The magnitude-matched foil is what stops Arm B from
                  re-measuring Arm A.

Generates no render. Resumable: completed rows are skipped. Guards halt an arm, never the run.

    python experiments/judge_damage_style_run.py --renders "<...>\\benchmark_mappa\\renders" \
        --model qwen3.8:27b --arm all
"""
import argparse, collections, csv, datetime, itertools, os, pathlib, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_multi_image import ask, ab, b64, guard

OUT = pathlib.Path("data/damage_style_answers.csv")
GATE = pathlib.Path("data/damage_style_gate.csv")
DISP = pathlib.Path("data/sign_decomposition_cells.csv")
BLOCKS = [f"Block_{i}" for i in range(1, 7)]
DOSES = ["0.050", "0.200"]
SIGNS = ["pos", "neg"]
PROMPTS = ["P01", "P02"]
SEEDS = ["42", "777", "1337"]

Q_DAMAGE = ("These are two versions of the same picture. One of them has visible rendering "
            "defects: smeared or mushy texture, broken shapes, colour banding or artefacts. "
            "Which one has more of those defects? Answer only A or B.")
Q_STYLE = ("The first image was produced by one particular image processing. Two more images "
           "follow, of a different subject. Which of them was produced by the SAME processing "
           "as the first image? Answer only A or B.")

FIELDS = ["judge_model", "url", "run_utc", "arm", "item_id", "order", "block", "dose", "sign",
          "prompt", "seed", "foil_block", "expected", "answer_raw", "choice", "hit"]


def path(renders, prompt, region, sign, dose, seed):
    if region == "baseline":
        return os.path.join(renders, f"{prompt}_baseline_krea2_seed{seed}_00001_.png")
    return os.path.join(renders, f"{prompt}_{region}{sign}_{dose}_krea2_seed{seed}_00001_.png")


def foil_table():
    """For each (dose, block): the other block whose mean ||D|| at that dose is closest.
    Read from the pixel decomposition already committed. Deterministic, no judgement."""
    if not DISP.exists():
        sys.exit(f"missing {DISP}; run experiments/sign_decomposition_pixels.py first")
    g = collections.defaultdict(list)
    for r in csv.DictReader(DISP.open(encoding="utf-8")):
        g[(r["region"], r["dose"])].append(
            (float(r["norm_plus"]) ** 2 + float(r["norm_minus"]) ** 2) / 2)
    norm = {k: float(np.mean(v)) ** 0.5 for k, v in g.items()}
    out = {}
    for d in DOSES:
        for b in BLOCKS:
            cand = [(abs(norm[(b, d)] - norm[(o, d)]), o) for o in BLOCKS if o != b]
            out[(b, d)] = min(cand)[1]
    return out


def items_A(renders):
    out = []
    # the null runs FIRST -- guard G3
    for p in PROMPTS:
        for s1, s2 in itertools.combinations(SEEDS, 2):
            out.append(dict(arm="A_null", item_id=f"Anull|{p}|{s1}|{s2}", block="", dose="",
                            sign="", prompt=p, seed=f"{s1}+{s2}", foil_block="",
                            imgs=(path(renders, p, "baseline", "", "", s1),
                                  path(renders, p, "baseline", "", "", s2))))
    for b, d, sg, p, s in itertools.product(BLOCKS, DOSES, SIGNS, PROMPTS, SEEDS):
        out.append(dict(arm="A", item_id=f"A|{b}|{d}|{sg}|{p}|{s}", block=b, dose=d, sign=sg,
                        prompt=p, seed=s, foil_block="",
                        imgs=(path(renders, p, "baseline", "", "", s),
                              path(renders, p, b, sg, d, s))))
    return out


def items_B(renders, foils):
    out = []
    for b, d, sg, s in itertools.product(BLOCKS, DOSES, SIGNS, SEEDS):
        fb = foils[(b, d)]
        out.append(dict(arm="B", item_id=f"B|{b}|{d}|{sg}|{s}", block=b, dose=d, sign=sg,
                        prompt="P01>P02", seed=s, foil_block=fb,
                        ref=path(renders, "P01", b, sg, d, s),
                        imgs=(path(renders, "P02", b, sg, d, s),
                              path(renders, "P02", fb, sg, d, s))))
    # null: neither candidate matches the reference
    for b, d, sg in itertools.product(BLOCKS[:3], DOSES, SIGNS):
        o = [x for x in BLOCKS if x != b]
        out.append(dict(arm="B_null", item_id=f"Bnull|{b}|{d}|{sg}", block=b, dose=d, sign=sg,
                        prompt="P01>P02", seed="42", foil_block=f"{o[0]}+{o[1]}",
                        ref=path(renders, "P01", b, sg, d, "42"),
                        imgs=(path(renders, "P02", o[0], sg, d, "42"),
                              path(renders, "P02", o[1], sg, d, "42"))))
    return out


def run(a, items, done, rows, halted):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    prog_log = pathlib.Path("data/damage_style_progress.log")
    t0 = time.time()
    this_run_calls = 0
    total_calls = len(items) * 2

    def log_progress(msg: str):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        with prog_log.open("a", encoding="utf-8") as pf:
            pf.write(line + "\n")

    new = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for it in items:
            if it["arm"] in halted:
                continue
            for order in (0, 1):
                key = (it["item_id"], str(order))
                if key in done:
                    continue
                missing = [q for q in (it["imgs"] + ((it["ref"],) if "ref" in it else ()))
                           if not os.path.exists(q)]
                if missing:
                    print(f"  SKIP {it['item_id']} order {order}: missing {os.path.basename(missing[0])}", flush=True)
                    continue
                first, second = it["imgs"] if order == 0 else it["imgs"][::-1]
                if "ref" in it:
                    imgs = [b64(it["ref"]), b64(first), b64(second)]
                    q = Q_STYLE
                    # in Arm B the TARGET is imgs[0] of the pair when order == 0
                    expected = "A" if order == 0 else "B"
                    if it["arm"] == "B_null":
                        expected = ""
                else:
                    imgs = [b64(first), b64(second)]
                    q = Q_DAMAGE
                    # in Arm A the PERTURBED image is imgs[1] when order == 0
                    expected = "B" if order == 0 else "A"
                    if it["arm"] == "A_null":
                        expected = ""
                try:
                    raw = ask(a.url, a.model, q, imgs)
                except Exception as exc:                       # unattended: record, never stop
                    print(f"  ERROR {it['item_id']} order {order}: {type(exc).__name__} {exc}", flush=True)
                    raw = ""
                ch = ab(raw)
                row = dict(judge_model=a.model, url=a.url, run_utc=stamp, arm=it["arm"],
                           item_id=it["item_id"], order=order, block=it["block"], dose=it["dose"],
                           sign=it["sign"], prompt=it["prompt"], seed=it["seed"],
                           foil_block=it["foil_block"], expected=expected,
                           answer_raw=(raw or "").replace("\n", " ")[:300], choice=ch,
                           hit=(int(ch == expected) if ch and expected else -1))
                w.writerow(row); fh.flush(); rows.append(row)
                done.add(key)
                this_run_calls += 1
                hit_str = 'hit' if row['hit']==1 else ('miss' if row['hit']==0 else '-')
                print(f"  [{len(rows)}/{total_calls}] {it['arm']:6s} {it['item_id']:34s} o{order} -> {ch or '?'}  {hit_str}", flush=True)

                if len(rows) % 10 == 0 or len(rows) == total_calls:
                    elapsed = time.time() - t0
                    rate = elapsed / max(1, this_run_calls)
                    rem_sec = (total_calls - len(rows)) * rate
                    log_progress(f"[RUN PROGRESS] Chiamate completate: {len(rows)}/{total_calls} (mancanti: {total_calls - len(rows)}) | Tempo trascorso: {elapsed/60:.1f}m | Stima residua: {rem_sec/60:.1f}m")

                for arm in ("A", "B"):
                    if arm in halted:
                        continue
                    ok, msg = guard(rows, arm)
                    if not ok:
                        print("  !! " + msg + " -- arm halted, recorded, the other arm continues", flush=True)
                        halted.add(arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:11434")
    ap.add_argument("--arm", default="all", choices=["all", "A", "B"])
    a = ap.parse_args()
    if not GATE.exists():
        sys.exit("the multi-image gate has not been run: experiments/judge_pairs_gate.py")
    done, rows = set(), []
    if OUT.exists():
        for r in csv.DictReader(OUT.open(encoding="utf-8")):
            if r["judge_model"] == a.model:
                done.add((r["item_id"], r["order"])); rows.append(r)
        print(f"resuming: {len(done)} answers already on disk")
    foils = foil_table()
    print("magnitude-matched foils, from data/sign_decomposition_cells.csv:")
    for d in DOSES:
        print(f"  dose {d}: " + ", ".join(f"{b}->{foils[(b,d)]}" for b in BLOCKS))
    halted = set()
    todo = []
    if a.arm in ("all", "A"):
        todo += items_A(a.renders)
    if a.arm in ("all", "B"):
        todo += items_B(a.renders, foils)
    run(a, todo, done, rows, halted)
    # G3: the Arm A null must sit inside [0.30, 0.70]
    nul = [r for r in rows if r["arm"] == "A_null" and r["choice"]]
    if nul:
        sh = sum(1 for r in nul if r["choice"] == "A") / len(nul)
        print(f"\nG3  Arm A null (baseline vs baseline): A-share {sh:.3f} over {len(nul)} calls "
              f"-> {'PASS' if 0.30 <= sh <= 0.70 else 'FAIL, Arm A is not interpretable'}")
    if halted:
        print(f"\nHALTED ARMS (this is a result, not an error): {sorted(halted)}")
    print(f"\ndone. answers in {OUT}")


if __name__ == "__main__":
    main()
