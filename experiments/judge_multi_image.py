#!/usr/bin/env python3
"""Shared helpers for multi-image forced-choice judging over Ollama.

Pre-registration: docs/prereg_damage_or_style.md (2026-09-27), frozen before any call.
Every question is forced choice, both orders, no absolute rating -- the rule established in
docs/prereg_capability_judge_amendment_02.md section 5 after 920 wasted calls.
"""
import base64, json, re, urllib.request

def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()

def ask(url, model, prompt, images, timeout=600):
    """images: list of base64 strings. Ollama shows them to the model in order."""
    body = json.dumps({"model": model, "prompt": prompt, "images": images,
                       "stream": False, "options": {"temperature": 0, "seed": 0}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()).get("response", "")

def ab(text):
    """Parse a forced choice. Returns 'A', 'B' or '' (unparseable)."""
    t = (text or "").strip()
    m = re.match(r'^\W*(?:image\s+|picture\s+|the\s+)?([ab])\b', t, re.I)
    if m:
        return m.group(1).upper()
    words = re.sub(r"[^A-Za-z]", " ", t).split()
    hits = [w.upper() for w in words if w.upper() in ("A", "B")]
    return hits[0] if len(set(hits)) == 1 and hits else ""

def guard(rows, arm, n=32, lo=0.25, hi=0.75, maxbad=0.10):
    """Pre-flight distributional guards G1 and G2. Returns (ok, message).
    Runs on the FIRST n calls of an arm, never only in the analysis."""
    sub = [r for r in rows if r["arm"] == arm][:n]
    if len(sub) < n:
        return True, f"{arm}: only {len(sub)} calls so far, guard not due"
    bad = sum(1 for r in sub if r["choice"] == "") / len(sub)
    if bad >= maxbad:
        return False, f"G2 FAILED {arm}: {bad:.2%} unparseable in the first {n} calls"
    good = [r for r in sub if r["choice"]]
    share = sum(1 for r in good if r["choice"] == "A") / len(good)
    if not (lo <= share <= hi):
        return False, f"G1 FAILED {arm}: first-position share {share:.3f} outside [{lo},{hi}]"
    return True, f"{arm}: guards pass ({bad:.2%} unparseable, A-share {share:.3f})"
