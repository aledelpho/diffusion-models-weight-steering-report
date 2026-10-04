"""Eye sheets for C45, one per arm and subject, built before any number is shown.

Rows: W1 original, W2 reordered, W3 tags, W4 synonyms, C1 content change.
Columns: seed 3141592 baseline | arm | seed 1234567 baseline | arm.
Alessandro marks per arm: same change across writings yes/partly/no; same change after
the content change yes/partly/no (docs/prereg_prompt_writing.md, "The eye").
  python experiments/prompt_writing_eye_sheets.py   -> benchmark_prompt_writing/_eye/*.jpg
"""
import os
from PIL import Image, ImageDraw
from analyze_prompt_writing import WRIT, CONTENT, SEEDS, PW, path, plan

W, H = 300, 375


def main():
    out = os.path.join(PW, "_eye"); os.makedirs(out, exist_ok=True)
    for c in [c for c in plan() if c != "baseline"]:
        for subj in ("S1", "S2"):
            pids = WRIT[subj] + [CONTENT[subj]]
            S = Image.new("RGB", (4 * W, len(pids) * (H + 18)), "white"); d = ImageDraw.Draw(S)
            for i, pid in enumerate(pids):
                for j, (cond, s) in enumerate([("baseline", SEEDS[0]), (c, SEEDS[0]), ("baseline", SEEDS[1]), (c, SEEDS[1])]):
                    p = path(pid, cond, s); y = i * (H + 18)
                    d.text((j * W + 3, y + 3), f"{pid} | {cond} | {s}", fill="black")
                    if os.path.exists(p):
                        S.paste(Image.open(p).convert("RGB").resize((W, H)), (j * W, y + 18))
                    else:
                        d.text((j * W + 3, y + 40), "MISSING", fill="red")
            S.save(os.path.join(out, f"{c}_{subj}.jpg"), quality=88)
    print("sheets in", out)


if __name__ == "__main__":
    main()
