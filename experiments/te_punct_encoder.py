"""C78 encoder-side measure — does punctuation (comma, period, semicolon, nopunct, nolabels) change
same-part vs cross-part token cosine similarity across the 12 taps of Qwen3-VL-4B?
Pre-registered in docs/prereg_te_punct.md ("for each tap, the mean cosine similarity of tokens of the
same part minus that of tokens of different parts, by version. Expected: larger with periods than commas
from layer 11 on. Reported, not a test.") and listed as pending in docs/te_punct_result.md.

Usage:
  python te_punct_encoder.py --gate      # bit-exact check against benchmark_te_conditioning/elf/P1_elfbrawler_baseline.npz
  python te_punct_encoder.py --run       # computes data/te_punct_encoder_by_tap.csv and data/te_punct_encoder_summary.csv
  python te_punct_encoder.py --selftest  # unit test on synthetic part-structured vectors
"""
import argparse, csv, json, re, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
COMFY_ROOT = Path(r"D:\StabilityMatrix-win-x64\Data\Packages\ComfyUI")
sys.path.insert(0, str(COMFY_ROOT))

import blk23_colorful as c47
import te_conditioning as TC
import te_punct as P1
import te_punct2 as P2

DATA = HERE.parent / "data"
OUT_TAP = DATA / "te_punct_encoder_by_tap.csv"
OUT_SUM = DATA / "te_punct_encoder_summary.csv"
TAPS = TC.TAPS  # [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]


def load_krea2_clip():
    import comfy.sd
    return comfy.sd.load_clip(ckpt_paths=[str(TC.TE_WEIGHTS)], clip_type=comfy.sd.CLIPType.KREA2, model_options={})


def encode_taps(clip, text):
    """Exact replica of Krea2ConditioningProbe.probe() in mode='full'."""
    import torch
    tokens = clip.tokenize(text)
    out = clip.encode_from_tokens(tokens, return_pooled=False, return_dict=True)
    cond = out["cond"]  # (1, seq, 12 * 2560)
    seq = cond.shape[1]
    c = cond[0].float().reshape(seq, 12, -1).cpu().numpy()
    key = next(iter(tokens))
    ids = [int(t[0]) if not torch.is_tensor(t[0]) else -1 for t in tokens[key][0]]
    ids = np.array(ids[-seq:], dtype=np.int64)
    return c.astype(np.float16).astype(np.float32), c.astype(np.float16), ids


def gate():
    clip = load_krea2_clip()
    elf_text = next(r["prompt_text"] for r in TC.rd(DATA / "te_pilot_plan.csv"))
    _, c_fp16, ids = encode_taps(clip, elf_text)
    ref_path = TC.out_path("elf", "P1_elfbrawler", "baseline")
    ref = np.load(ref_path)
    same_cond = np.array_equal(c_fp16, ref["cond"])
    same_ids = np.array_equal(ids, ref["ids"])
    max_diff = float(np.abs(c_fp16.astype(np.float32) - ref["cond"].astype(np.float32)).max())
    print(f"P1_elfbrawler_baseline vs C67 .npz: cond bit-identical={same_cond}, ids bit-identical={same_ids}, max_abs_diff={max_diff}")
    ok = same_cond and same_ids and max_diff == 0.0
    print("GATE", "PASS" if ok else "FAIL - stop")
    if not ok:
        sys.exit(1)
    return clip


def assign_parts_by_char_span(ids, inv, full_text, part_strings):
    """Map each content token (before <|im_end|>) to its part index 0..M-1 by exact character span in full_text.
    Separator tokens between parts and label prefixes (if excluded from part_strings) get part_idx = -1."""
    pieces = [inv.get(int(i), "") for i in ids]
    end = next((p for p, s in enumerate(pieces) if s.startswith("<|im_end")), len(pieces))
    recon = "".join(pieces[:end])
    assert recon == full_text, f"Token reconstruction mismatch:\n  recon={recon!r}\n  text ={full_text!r}"

    # Find exact non-overlapping character spans of each part_string in order
    spans = []
    cursor = 0
    for m, pstr in enumerate(part_strings):
        idx = full_text.find(pstr, cursor)
        assert idx != -1, f"Part {m} not found in text starting at {cursor}: {pstr[:40]!r}"
        spans.append((idx, idx + len(pstr), m))
        cursor = idx + len(pstr)

    part_of = np.full(end, -1, dtype=np.int32)
    pos_char = 0
    for p in range(end):
        tok_str = pieces[p]
        tok_start = pos_char
        tok_end = pos_char + len(tok_str)
        pos_char = tok_end
        # Strip leading/trailing whitespace and punctuation from the token when checking if it is a content token
        stripped = re.sub(r"^[\s,.;:\n\r]+|[\s,.;:\n\r]+$", "", tok_str)
        if not stripped:
            continue
        # Find where the alphanumeric core of the token sits
        core_offset = tok_str.find(stripped)
        core_mid = tok_start + core_offset + len(stripped) / 2.0
        for s_start, s_end, m in spans:
            if s_start <= core_mid < s_end:
                part_of[p] = m
                break
    return part_of, end


def same_minus_cross(X, part_of):
    """Mean cosine similarity of token pairs in the same part minus token pairs in different parts.
    Only tokens with part_of >= 0 are included."""
    keep = np.where(part_of >= 0)[0]
    Xk = X[keep]
    pk = part_of[keep]
    norms = np.linalg.norm(Xk, axis=1, keepdims=True) + 1e-12
    Y = Xk / norms
    C = Y @ Y.T
    n = len(keep)
    iu, ju = np.triu_indices(n, k=1)
    same_mask = pk[iu] == pk[ju]
    diff_mask = ~same_mask
    assert same_mask.any() and diff_mask.any(), "Need both same-part and cross-part token pairs"
    same_mean = float(C[iu[same_mask], ju[same_mask]].mean())
    cross_mean = float(C[iu[diff_mask], ju[diff_mask]].mean())
    return same_mean, cross_mean, same_mean - cross_mean


def build_prompt_sets():
    """Returns list of (set_name, prompt_id, version, full_text, part_strings_all, part_strings_chars_only)."""
    items = []
    # 1. Built prompts P1 and P2 (4 parts each)
    for pid, parts in P1.BUILT.items():
        for v, sep in (("comma", ", "), ("period", ". "), ("semicolon", "; "), ("nopunct", " ")):
            full_text = sep.join(parts)
            items.append(("built_4parts", pid, v, full_text, parts, None))

    # 2. Complex 4-character prompts P3_totem and P4_prison (7 paragraphs total; paragraphs 1..4 are Characters 1..4)
    for pid, png in P2.SOURCES.items():
        orig = P2.source_text(png)
        raw_paras = P2.paragraphs(orig)
        assert len(raw_paras) == 7, (pid, len(raw_paras))
        # Strip the "Character N (...):" / section label from the core content of each part so that
        # 'nolabels' and 'original' compare the exact same content words!
        body_paras = [P2.LABEL.sub("", p).rstrip(".") for p in raw_paras]
        for v in ["original", "comma", "period", "semicolon", "nopunct", "nolabels"]:
            full_text = orig if v == "original" else P2.version_text(orig, v)
            # Transform each part body with the exact same within-part punctuation rule so substrings match verbatim
            if v in ("original", "comma"):
                v_parts = [re.sub(r"\.\s+", ", ", b) if v == "comma" else b for b in body_paras]
            elif v == "period":
                v_parts = [b.replace(", ", ". ") for b in body_paras]
            elif v == "semicolon":
                v_parts = [b.replace(", ", "; ") for b in body_paras]
            elif v == "nopunct":
                v_parts = [re.sub(r"\s+", " ", re.sub(r"[,.;:\n\r]+", " ", b)).strip() for b in body_paras]
            elif v == "nolabels":
                v_parts = list(body_paras)
            items.append(("complex_all7", pid, v, full_text, v_parts, v_parts[1:5]))
    return items


def run():
    clip = gate()
    inv = TC.vocab()
    items = build_prompt_sets()
    tap_rows = []

    for set_name, pid, v, full_text, parts_all, parts_chars in items:
        c, _, ids = encode_taps(clip, full_text)
        scopes = [("all_parts", parts_all)]
        if parts_chars is not None:
            scopes.append(("chars_1to4", parts_chars))

        for scope_name, part_list in scopes:
            part_of, end = assign_parts_by_char_span(ids, inv, full_text, part_list)
            counts_per_part = [int((part_of == m).sum()) for m in range(len(part_list))]
            assert all(cnt > 0 for cnt in counts_per_part), (pid, v, scope_name, counts_per_part)

            for t_idx, layer in enumerate(TAPS):
                Xt = c[:end, t_idx, :]  # (end, 2560)
                # 1. Raw conditioning vectors (as pre-registered)
                s_raw, x_raw, d_raw = same_minus_cross(Xt, part_of)
                # 2. Position-centred conditioning vectors (removing prompt-wide shared mean / massive activations)
                Xt_cent = Xt - Xt.mean(axis=0, keepdims=True)
                s_cnt, x_cnt, d_cnt = same_minus_cross(Xt_cent, part_of)

                tap_rows.append({
                    "set": set_name,
                    "scope": scope_name,
                    "prompt_id": pid,
                    "version": v,
                    "tap_idx": t_idx,
                    "tap_layer": layer,
                    "n_tokens_used": int((part_of >= 0).sum()),
                    "same_cos_raw": round(s_raw, 5),
                    "cross_cos_raw": round(x_raw, 5),
                    "same_minus_cross_raw": round(d_raw, 5),
                    "same_cos_centred": round(s_cnt, 5),
                    "cross_cos_centred": round(x_cnt, 5),
                    "same_minus_cross_centred": round(d_cnt, 5),
                })

    with open(OUT_TAP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tap_rows[0]))
        w.writeheader()
        w.writerows(tap_rows)

    # Build summary table across taps >= 11 (layers 11..35, i.e. taps 3..11, as pre-registered: "from layer 11 on")
    # and across all 12 taps
    summary_rows = []
    groups = sorted({(r["set"], r["scope"], r["version"]) for r in tap_rows})
    for set_name, scope_name, v in groups:
        sub_all = [r for r in tap_rows if r["set"] == set_name and r["scope"] == scope_name and r["version"] == v]
        sub_l11 = [r for r in sub_all if r["tap_layer"] >= 11]
        summary_rows.append({
            "set": set_name,
            "scope": scope_name,
            "version": v,
            "mean_diff_raw_all12": round(float(np.mean([r["same_minus_cross_raw"] for r in sub_all])), 5),
            "mean_diff_raw_L11_to_L35": round(float(np.mean([r["same_minus_cross_raw"] for r in sub_l11])), 5),
            "mean_diff_centred_all12": round(float(np.mean([r["same_minus_cross_centred"] for r in sub_all])), 5),
            "mean_diff_centred_L11_to_L35": round(float(np.mean([r["same_minus_cross_centred"] for r in sub_l11])), 5),
        })

    with open(OUT_SUM, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0]))
        w.writeheader()
        w.writerows(summary_rows)

    print(f"Wrote {len(tap_rows)} rows to {OUT_TAP.name} and {len(summary_rows)} rows to {OUT_SUM.name}")
    for r in summary_rows:
        print(r)


def selftest():
    rng = np.random.default_rng(42)
    # 4 parts of 5 tokens each; tokens in the same part share a cluster vector
    clusters = rng.normal(size=(4, 64))
    X = np.vstack([clusters[m] + 0.2 * rng.normal(size=(5, 64)) for m in range(4)])
    part_of = np.repeat(np.arange(4), 5)
    s, x, d = same_minus_cross(X, part_of)
    assert d > 0.5 and s > x, (s, x, d)
    print("selftest ok:", round(s, 3), round(x, 3), round(d, 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for x in ("gate", "run", "selftest"):
        ap.add_argument(f"--{x}", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    if a.gate:
        gate()
    if a.run:
        run()
