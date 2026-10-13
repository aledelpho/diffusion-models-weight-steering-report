"""C74 tally (docs/prereg_te_dose.md). Written 2026-10-13, before any C74 label. Input: data/te_dose_alessandro.csv
(committed as downloaded), columns grid,row,cambia_da,come,verso,coerenza_da,note. Output: data/te_dose_tests.csv.

  python te_dose_tally.py
  python te_dose_tally.py --selftest
"""
import argparse, csv
from collections import Counter
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
ORDER = {d: i for i, d in enumerate(["0.10", "0.25", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.85", "0.90", "0.95", "1.00"], 1)}
ORDER["mai"] = 99   # amendment 1: twelve doses


def tally(rows):
    out = []
    main = [r for r in rows if r["grid"] in ("dose_L06", "dose_L14")]
    ch = [r for r in main if r.get("cambia_da") and r["cambia_da"] != "mai"]
    # H1 gradual vs step
    g = [r["come"] for r in ch if r.get("come") in ("graduale", "scatto")]
    sh = sum(x == "graduale" for x in g) / len(g) if g else None
    h1 = "inconclusive (no labels)" if sh is None else ("gradual supported" if sh >= 0.6 else ("step-like supported" if sh <= 0.3 else "inconclusive"))
    out.append({"test": "H1 gradual vs step (L06, L14)", "value": f"graduale {sum(x == 'graduale' for x in g)} of {len(g)} changing strips" + (f" = {sh:.2f}" if sh is not None else ""), "verdict": h1})
    # H2 direction
    v = [r["verso"] for r in ch if r.get("verso") in ("sì", "no", "incerto")]
    sv = sum(x == "sì" for x in v) / len(v) if v else None
    h2 = "inconclusive (no labels)" if sv is None else ("supported" if sv >= 0.7 else ("not supported" if sv <= 0.4 else "inconclusive"))
    out.append({"test": "H2 intermediate doses move toward the d = 1.00 picture", "value": f"sì {sum(x == 'sì' for x in v)} of {len(v)}" + (f" = {sv:.2f}" if sv is not None else ""), "verdict": h2})
    # H3 style before coherence loss
    both = [r for r in ch if r.get("coerenza_da")]
    before = sum(ORDER[r["cambia_da"]] < ORDER[r["coerenza_da"]] for r in both)
    after = sum(ORDER[r["coerenza_da"]] <= ORDER[r["cambia_da"]] for r in both)
    n = len(both)
    h3 = ("inconclusive (no labels)" if not n else ("style moves before coherence breaks: supported" if before >= 2 * n / 3
          else ("the change is mainly a loss of coherence: supported" if after >= 2 * n / 3 else "inconclusive")))
    out.append({"test": "H3 style change before loss of coherence", "value": f"before {before}, at or after {after}, of {n}", "verdict": h3})
    # reported
    for L in ("dose_L06", "dose_L14", "dose_L28"):
        rs = [r for r in rows if r["grid"] == L]
        out.append({"test": f"{L} (reported)", "value": f"onset {dict(Counter(r.get('cambia_da', '') for r in rs))}; how {dict(Counter(r.get('come', '') for r in rs))}; "
                    f"toward 1.00 {dict(Counter(r.get('verso', '') for r in rs))}; coherence lost from {dict(Counter(r.get('coerenza_da', '') for r in rs))}", "verdict": ""})
    return out


def run():
    out = tally(list(csv.DictReader(open(DATA / "te_dose_alessandro.csv", encoding="utf-8"))))
    with open(DATA / "te_dose_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "value", "verdict"]); w.writeheader(); w.writerows(out)
    for o in out: print(o)


def selftest():
    rows = []
    for L in ("dose_L06", "dose_L14"):
        for i in range(6):
            rows.append({"grid": L, "row": str(i), "cambia_da": "0.25", "come": "graduale" if i < 5 else "scatto", "verso": "sì", "coerenza_da": "1.00" if i < 4 else "0.25"})
    for i in range(6):
        rows.append({"grid": "dose_L28", "row": str(i), "cambia_da": "mai", "come": "nessuno", "verso": "nessuno", "coerenza_da": "mai"})
    d = {o["test"].split(" ")[0]: o for o in tally(rows)}
    assert d["H1"]["verdict"] == "gradual supported", d["H1"]
    assert d["H2"]["verdict"] == "supported"
    assert d["H3"]["verdict"].startswith("style moves before"), d["H3"]     # 8 of 12 before
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else run()
