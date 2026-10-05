"""Export the results notebook (results/) as a standalone repository.

Usage (from the root of the main repository, after it has been pushed):

    python experiments/export_results_repo.py --sha <full commit sha on origin/main> --out <empty folder>

What it does:
  * copies results/20-*.md ... results/27-*.md to the root of --out, and writes a new README.md;
  * copies the figures those pages show (assets/<page>/...) and every data/ file they cite;
  * rewrites links that point outside results/ (../notebook/, docs/, experiments/) into absolute
    GitHub links to the main repository, pinned to --sha, so they never drift;
  * copies LICENSE;
  * checks the output: every relative link and image resolves, no '../' is left, every cited
    data/ file exists. Exit code 1 on any failure; nothing is pushed or committed.

It does not create the repository, commit or push. Those are separate, manual steps.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
MAIN = "https://github.com/aledelpho/diffusion-models-weight-steering-report"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sha", required=True, help="full commit sha of the main repository, already on GitHub")
    ap.add_argument("--out", required=True, help="output folder (must not exist or be empty)")
    ap.add_argument("--allow-unpushed", action="store_true",
                    help="test run only: skip the check that --sha is on origin/main (links will be dead)")
    a = ap.parse_args()

    sha = a.sha.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        sys.exit("--sha must be a full 40-character commit sha")
    # The sha must exist locally and be contained in origin/main, otherwise every link is dead.
    ok = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "origin/main"], cwd=ROOT)
    if ok.returncode != 0 and not a.allow_unpushed:
        sys.exit(f"{sha} is not on origin/main: push the main repository first, then fetch")

    out = Path(a.out).resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} is not empty")
    out.mkdir(parents=True, exist_ok=True)

    blob = f"{MAIN}/blob/{sha}/"
    pages = sorted(p for p in RESULTS.glob("2*.md"))
    data_needed: set[str] = set()
    errors: list[str] = []

    def rewrite(text: str) -> str:
        # Markdown links/images to the notebook and to assets.
        text = re.sub(r"\]\(\.\./notebook/([^)]+)\)", lambda m: f"]({blob}notebook/{m.group(1)})", text)
        text = text.replace("](../assets/", "](assets/")
        # Inline-code paths into docs/ and experiments/ become pinned links.
        def code_link(m):
            path = m.group(1)
            if (ROOT / path).exists():
                return f"[`{path}`]({blob}{path})"
            errors.append(f"cited path not in the main repository: {path}")
            return m.group(0)
        text = re.sub(r"(?<!\[)`((?:docs|experiments|presets)/[\w./-]+)`", code_link, text)
        return text

    for p in pages:
        t = p.read_text(encoding="utf-8")
        data_needed |= set(re.findall(r"data/[\w./-]+\.(?:csv|md|npz|jsonl)", t))
        (out / p.name).write_text(rewrite(t), encoding="utf-8")
        page_assets = ROOT / "assets" / p.stem
        if page_assets.exists():
            shutil.copytree(page_assets, out / "assets" / p.stem)

    for d in sorted(data_needed):
        src = ROOT / d
        if not src.exists():
            errors.append(f"cited data file missing: {d}")
            continue
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", d], cwd=ROOT,
                                 capture_output=True).returncode == 0
        if not tracked:
            errors.append(f"cited data file is not committed in the main repository: {d}")
        (out / d).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out / d)

    shutil.copy2(ROOT / "LICENSE", out / "LICENSE")

    # README: the main repo's results/README.md, with a provenance header.
    readme = (RESULTS / "README.md").read_text(encoding="utf-8")
    readme = rewrite(readme).replace("[`../notebook/`](../notebook/)", f"[`notebook/`]({MAIN}/tree/{sha}/notebook)")
    readme = readme.replace("this folder holds only", "this repository holds only")
    header = (
        "> **Where this comes from.** This repository holds the final results of the project. "
        f"The exploratory notebook, the pre-registrations, the analysis scripts and every other "
        f"experiment live in [the main repository]({MAIN}); every link to it is pinned to commit "
        f"[`{sha[:7]}`]({MAIN}/tree/{sha}), so what you read here is what was there when these pages "
        "were published. The data files the pages cite are copied in `data/`.\n\n"
    )
    first_break = readme.find("\n\n") + 2
    (out / "README.md").write_text(readme[:first_break] + header + readme[first_break:], encoding="utf-8")

    # Checks on the output.
    for md in out.glob("*.md"):
        t = md.read_text(encoding="utf-8")
        if "../" in t:
            errors.append(f"{md.name}: a '../' link is left")
        for target in re.findall(r"\]\(([^)\s]+)\)", t):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            f = (out / target.split("#", 1)[0]).resolve()
            if not f.exists():
                errors.append(f"{md.name}: link or image does not resolve: {target}")
        for d in re.findall(r"data/[\w./-]+\.(?:csv|md|npz|jsonl)", t):
            if not (out / d).exists():
                errors.append(f"{md.name}: cites {d}, not in the export")

    n_files = sum(1 for _ in out.rglob("*") if _.is_file())
    print(f"exported {len(pages)} pages, {len(data_needed)} data files, {n_files} files in total -> {out}")
    if errors:
        for e in sorted(set(errors)):
            print("  ERROR", e)
        return 1
    print("  PASS -- every link and image resolves; no '../' left; every cited data file present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
