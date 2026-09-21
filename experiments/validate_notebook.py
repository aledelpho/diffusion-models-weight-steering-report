#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_notebook.py -- the checks behind notebook/AUTHORING.md.

A rule that is not enforced is a rule that will be broken. This project has the receipts:
pitfall 30 (two runs sharing an output root) has recurred twice, and rule 15 (analyse every
arm already on disk) was broken the same afternoon it was written. So the contract in
AUTHORING.md is checked here rather than trusted.

    python experiments/validate_notebook.py                 # everything
    python experiments/validate_notebook.py --page 05-knob-or-cost
    python experiments/validate_notebook.py --strict        # warnings become failures

Exit code 0 when no ERROR was raised. WARN never fails unless --strict.

Dependencies: PyYAML. Pillow only for the dark-background check, which is skipped with a
notice when Pillow or the figure files are absent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("validate_notebook.py needs PyYAML:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))   # so extract_repro imports
NOTEBOOK = ROOT / "notebook"
FIGURES_YAML = ROOT / "experiments" / "figures.yaml"
ASSETS = ROOT / "assets"

VALID_STATUS = {"holds", "ambiguous", "overturned", "open"}
VALID_STAGE = {"exploratory", "confirmatory", "verification"}
VALID_KIND = {"scatter", "strip", "toggle", "contact_sheet", "ramp",
              "diffmap", "paired_bars", "schema"}

REQUIRED_FRONT_MATTER = ["id", "title", "status", "stage", "date",
                         "preregistration", "supersedes", "pitfalls", "corpus", "claims"]

REQUIRED_SECTIONS = ["In two minutes", "The verdict", "Why I might be wrong",
                     "The data", "Provenance"]

REPRO_KEYS = ["model", "sampling", "tuner", "prompts", "seeds",
              "conditions", "outputs", "analysis"]

SURFACE_RGB = (0x1a, 0x1a, 0x19)
SURFACE_TOLERANCE = 24          # per channel; a dark theme that drifted slightly still passes
CADENCE_MAX_PARAGRAPHS = 4

# Function words that are common in Italian and rare-to-absent in English prose.
# "e", "a", "in", "no", "media" and similar are deliberately excluded: they are English words
# too, or appear inside identifiers, and would fire on clean pages. "come" and
# "stato" were removed after firing on correct English prose: a check that cries
# wolf on a clean page gets ignored, which is worse than not having it.
ITALIAN_MARKERS = {
    "perche", "perché", "quando", "questo", "questa", "questi", "queste", "della", "dello",
    "delle", "degli", "nella", "nelle", "nello", "sono", "essere", "anche",
    "invece", "quindi", "soltanto", "abbiamo", "stata", "viene",
    "vengono", "misura", "misurato", "spostamento", "immagine", "immagini", "blocchi",
    "prova", "risultato", "risultati", "senza", "ancora", "ogni", "che", "non", "piu",
    "più", "cosa", "dove", "sulla", "sulle", "dalla", "dalle", "negli", "fra",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warns: list[str] = []
        self.notes: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warns.append(f"{where}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def split_front_matter(text: str, path: Path, rep: Report):
    if not text.startswith("---"):
        rep.error(path.name, "no YAML front matter (the file must start with ---)")
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        rep.error(path.name, "front matter is not terminated by a --- line")
        return None, text
    raw, body = text[3:end], text[end + 4:]
    try:
        return yaml.safe_load(raw) or {}, body
    except yaml.YAMLError as exc:
        rep.error(path.name, f"front matter is not valid YAML: {exc}")
        return None, body


def slugify(heading: str) -> str:
    """GitHub's anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"[-\s]+", "-", s).strip("-")


def check_front_matter(fm: dict, path: Path, rep: Report) -> None:
    where = path.name

    for key in REQUIRED_FRONT_MATTER:
        if key not in fm:
            rep.error(where, f"front matter is missing required key '{key}'")

    if fm.get("id") != path.stem:
        rep.error(where, f"id '{fm.get('id')}' does not match the filename '{path.stem}'")

    status, stage = fm.get("status"), fm.get("stage")
    if status not in VALID_STATUS:
        rep.error(where, f"status '{status}' is not one of {sorted(VALID_STATUS)}")
    if stage not in VALID_STAGE:
        rep.error(where, f"stage '{stage}' is not one of {sorted(VALID_STAGE)}")

    # An exploratory result cannot hold. This is the distinction the notebook exists to keep.
    # "verification" is the third kind: an integrity check with a criterion fixed before the
    # value and a pass/fail outcome. It is not a hypothesis, so it needs no pre-registration,
    # and it can hold.
    if status == "holds" and stage == "exploratory":
        rep.error(where, "status 'holds' with stage 'exploratory' -- an exploratory result "
                         "cannot hold; use 'open' or 'ambiguous'")
    prereg = fm.get("preregistration")
    if stage == "confirmatory" and not prereg:
        rep.error(where, "stage 'confirmatory' requires a preregistration")
    # A pre-registration that names a file which is not in the repository is not a
    # pre-registration a reader can check. 05-knob-or-cost.md shipped for a day naming a
    # document that had never been committed, and nothing noticed.
    if prereg and not (ROOT / str(prereg)).exists():
        rep.error(where, f"preregistration '{prereg}' does not exist in the repository -- "
                         f"a frozen document nobody can open is not a frozen document")

    corpus = fm.get("corpus") or {}
    if not isinstance(corpus, dict) or "renders" not in corpus:
        rep.error(where, "corpus must be a mapping containing at least 'renders'")


def check_claims(fm: dict, body: str, path: Path, rep: Report) -> list[dict]:
    where = path.name
    claims = fm.get("claims") or []
    if not claims:
        rep.warn(where, "no claims declared -- this page contributes nothing to the index")
        return []

    anchors = {slugify(h) for h in re.findall(r"^#{1,6}\s+(.+)$", body, re.M)}
    seen = set()

    for claim in claims:
        cid = claim.get("id", "<no id>")
        if cid in seen:
            rep.error(where, f"claim id '{cid}' is declared twice")
        seen.add(cid)

        for key in ("statement", "evidence", "anchor", "status"):
            if not claim.get(key):
                rep.error(where, f"claim '{cid}' is missing '{key}'")

        if claim.get("status") not in VALID_STATUS:
            rep.error(where, f"claim '{cid}' has status '{claim.get('status')}'")

        anchor = (claim.get("anchor") or "").lstrip("#")
        if anchor and anchor not in anchors:
            rep.error(where, f"claim '{cid}' points at anchor '#{anchor}', "
                             f"which is not a heading on this page")

        stmt = (claim.get("statement") or "").strip()
        if stmt and len(stmt.split()) < 5:
            rep.warn(where, f"claim '{cid}' statement is very short -- "
                            f"a claim should be something a reader could disagree with")
    return claims


OPENING_LEAD_INS = ["The direction I'm chasing.",
                    "What would kill it.",
                    "Where we are."]


def check_opening_block(body: str, path: Path, rep: Report) -> None:
    """The three first-person lines above 'In two minutes' (AUTHORING.md section 2).

    Every experiment in the old README opened this way, and the migration nearly dropped the
    habit: a page that starts at the finding tells a reader what was measured and never why
    anyone cared. The check is structural only -- it cannot tell whether the third line is
    honest.
    """
    head = body.split("\n## In two minutes", 1)[0]
    quoted = "\n".join(l for l in head.splitlines() if l.lstrip().startswith(">"))
    at = -1
    for lead in OPENING_LEAD_INS:
        i = quoted.find(f"**{lead}**", at + 1)
        if i < 0:
            rep.error(path.name, f"the opening block is missing '**{lead}**' above "
                                 f"'## In two minutes' -- see AUTHORING.md section 2")
            return
        if i < at:
            rep.error(path.name, f"'**{lead}**' comes out of order in the opening block "
                                 f"(expected {OPENING_LEAD_INS})")
            return
        at = i


def check_header_corpus(fm: dict, body: str, path: Path, rep: Report) -> None:
    """The render count in the status line against `corpus.renders`.

    Three pages disagreed with themselves in their own header line until 2026-09-21: 421
    against 423, 670 against 870, and 168 against 368. A number written twice on one page is
    a number that will drift, so the two are now tied together.
    """
    m = re.search(r"^>\s+\*\*\w+\*\*\s*\u00b7\s*([\d,]+)\s+(?:renders|cells)", body, re.M)
    if not m:
        return
    shown = int(m.group(1).replace(",", ""))
    declared = (fm.get("corpus") or {}).get("renders")
    if isinstance(declared, int) and shown != declared:
        rep.error(path.name, f"the status line says {shown} renders, "
                             f"front matter says corpus.renders: {declared}")


def check_repro_against_data(fm: dict, body: str, path: Path, rep: Report) -> None:
    """Every field of the reproducibility block that a file in `data/` can prove.

    AUTHORING.md section 5 required this from the first day and named the script that would
    do it; the script did not exist, and an audit on 2026-09-21 found four hand-typed fields
    wrong across four pages -- a resolution, a displacement printed as a single number where
    the file holds six, a manifest that was never committed, and a note asserting a
    verification that had never run. The check is now here so that class of error cannot
    reach a reader again.
    """
    try:
        import extract_repro
    except Exception as exc:                                  # pragma: no cover
        rep.note(f"extract_repro could not be imported ({exc}); "
                 f"the reproducibility block was not checked against data/")
        return
    m = re.search(r"###\s+Reproducing this\s*\n+```ya?ml\n(.*?)```", body, re.S)
    if not m:
        return
    try:
        block = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return                                                # check_reproducibility reports it
    for bad in extract_repro.mismatches(str(fm.get("id")), block):
        rep.error(path.name, f"reproducibility block: {bad}")


def check_render_count(fm: dict, body: str, rep: Report, path: Path) -> None:
    """`corpus.renders` against the bench sizes the page itemises in Provenance.

    Where a page lists its benches with a count each, the front matter's total is arithmetic
    and can be checked. Page 05 read 386 against its own itemised 368 for a day.
    """
    m = re.search(r"^(?:\*\s*Renders:|\*\*Renders\.\*\*)(.+)$", body, re.M)
    if not m:
        return
    parts = [int(n) for n in re.findall(r"\((\d+)[,)]", m.group(1))]
    if not parts:
        return
    declared = (fm.get("corpus") or {}).get("renders")
    if isinstance(declared, int) and sum(parts) != declared:
        rep.error(path.name, f"corpus.renders is {declared}, but the Provenance line itemises "
                             f"{' + '.join(str(p) for p in parts)} = {sum(parts)}")


def check_sections(body: str, path: Path, rep: Report) -> None:
    headings = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, re.M)]
    order, missing = [], []
    for wanted in REQUIRED_SECTIONS:
        if wanted in headings:
            order.append(headings.index(wanted))
        else:
            missing.append(wanted)
    for m in missing:
        rep.error(path.name, f"missing required section '## {m}'")
    if len(order) == len(REQUIRED_SECTIONS) and order != sorted(order):
        rep.error(path.name, "the five required sections are present but out of order "
                             f"(expected {REQUIRED_SECTIONS})")


def check_reproducibility(body: str, path: Path, rep: Report) -> None:
    where = path.name
    m = re.search(r"###\s+Reproducing this\s*\n+```ya?ml\n(.*?)```", body, re.S)
    if not m:
        rep.error(where, "no '### Reproducing this' block with a yaml fence -- "
                         "a stranger with the checkpoint must be able to recreate the renders")
        return
    try:
        repro = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        rep.error(where, f"the reproducibility block is not valid YAML: {exc}")
        return

    for key in REPRO_KEYS:
        if key not in repro:
            rep.error(where, f"reproducibility block is missing '{key}'")

    for cond in repro.get("conditions") or []:
        if not isinstance(cond, dict):
            continue
        if "measured_D" not in cond:
            rep.error(where, f"condition '{cond.get('name')}' has no measured_D -- "
                             f"the measured displacement, never the nominal one (pitfall 13)")

    todos = len(re.findall(r"\bTODO\b", m.group(1)))
    if todos:
        rep.warn(where, f"reproducibility block still has {todos} TODO placeholder(s)")


def check_duplicate_columns(body: str, path: Path, rep: Report) -> None:
    """Two columns with different names and identical content read as two measurements.

    Pitfall 69: a missing control was filled with the nearest available one, and the duplicate
    was invisible in every reading of the report -- the strongest number on that page rested on
    it. Any CSV a page names is checked here, cheaply: same values on every row, different name.
    """
    import csv as _csv
    for rel in sorted(set(re.findall(r"`(data/[A-Za-z0-9_./-]+\.csv)`", body))):
        f = ROOT / rel
        if not f.exists():
            continue
        try:
            rows = list(_csv.DictReader(f.open(encoding="utf-8-sig", newline="")))
        except Exception:
            continue
        if len(rows) < 2:
            continue
        cols = [c for c in (rows[0] or {}) if c]
        numeric = {}
        for c in cols:
            try:
                numeric[c] = [float(r[c]) for r in rows]
            except (TypeError, ValueError):
                continue
        names = sorted(numeric)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if all(abs(x - y) < 1e-12 for x, y in zip(numeric[a], numeric[b])):
                    rep.error(path.name,
                              f"{rel}: columns '{a}' and '{b}' are identical on all "
                              f"{len(rows)} rows -- two names for one measurement read as two "
                              f"(pitfall 69). Leave a missing control empty, never fill it "
                              f"with the nearest one")


def check_language(body: str, path: Path, rep: Report) -> None:
    prose = re.sub(r"```.*?```", " ", body, flags=re.S)        # drop code fences
    prose = re.sub(r"`[^`]*`", " ", prose)                     # drop inline code
    prose = re.sub(r"\]\([^)]*\)", " ", prose)                 # drop link targets
    words = re.findall(r"[a-zA-ZàèéìòùÀÈÉÌÒÙ]+", prose.lower())
    hits = sorted({w for w in words if w in ITALIAN_MARKERS})
    if hits:
        rep.error(path.name, f"the notebook is written in English; Italian words found: "
                             f"{', '.join(hits[:8])}"
                             f"{'...' if len(hits) > 8 else ''}")


def check_cadence(body: str, path: Path, rep: Report) -> None:
    """One figure every two to four paragraphs. Reported, never failed."""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    run = 0
    worst = 0
    for block in [b.strip() for b in body.split("\n\n") if b.strip()]:
        if block.startswith(("#", ">", "|", "*", "-", "1.")):
            continue
        if re.search(r"!\[[^\]]*\]\([^)]+\)|<img", block):
            run = 0
            continue
        run += 1
        worst = max(worst, run)
    if worst > CADENCE_MAX_PARAGRAPHS:
        rep.warn(path.name, f"{worst} consecutive paragraphs without a figure "
                            f"(target is one every {CADENCE_MAX_PARAGRAPHS} or fewer)")


def load_registry(rep: Report) -> dict:
    if not FIGURES_YAML.exists():
        rep.error("experiments/figures.yaml", "the figure registry does not exist")
        return {}
    try:
        data = yaml.safe_load(FIGURES_YAML.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        rep.error("experiments/figures.yaml", f"not valid YAML: {exc}")
        return {}
    return {f["id"]: f for f in (data.get("figures") or []) if isinstance(f, dict) and "id" in f}


CROP_RE = re.compile(r"^(whole|locator:[a-z0-9_]+)$")
RECT_RE = re.compile(r"\d+\s*[,x]\s*\d+")


def check_registry(reg: dict, rep: Report) -> None:
    for fid, fig in sorted(reg.items()):
        where = f"figures.yaml[{fid}]"
        kind = fig.get("kind")

        if kind not in VALID_KIND:
            rep.error(where, f"kind '{kind}' is not one of {sorted(VALID_KIND)}")

        alt = (fig.get("alt") or "").strip()
        if not alt:
            rep.error(where, "no alt text -- write it as the claim the figure makes")
        elif len(alt.split()) < 8:
            rep.warn(where, "alt text is very short; it should state the claim, "
                            "not describe the picture")

        if kind == "schema":
            # A schema explains; it never carries a measured number.
            if fig.get("source"):
                rep.error(where, "a schema must not have a measurement source -- "
                                 "a figure carries numbers only if a script read them")
            if fig.get("caption_from") != "static":
                rep.error(where, "a schema must use caption_from: static")
        else:
            if not fig.get("source"):
                rep.error(where, "no source -- every evidence figure names the measurement "
                                 "file its numbers come from")
            if fig.get("caption_from") != "source":
                rep.error(where, "caption_from must be 'source': the caption is derived from "
                                 "the measurement of the image being drawn (pitfall 40)")
            if not fig.get("builder"):
                rep.error(where, "no builder function named")

        crop = str(fig.get("crop", ""))
        if not CROP_RE.match(crop):
            if RECT_RE.search(crop):
                rep.error(where, f"crop '{crop}' looks like a pixel rectangle. A crop is a "
                                 f"locator resolved per (prompt, condition, seed), never a "
                                 f"literal box -- seeds move the content (pitfall 40)")
            else:
                rep.error(where, f"crop must be 'whole' or 'locator:<name>', got '{crop}'")

        if kind == "toggle" and not fig.get("control"):
            rep.error(where, "a toggle needs a control pair (two baselines at different "
                             "seeds), so a reader can see how far the image moves when "
                             "nothing was touched")


def check_figure_files(reg: dict, rep: Report) -> None:
    """Sample the border of every built figure and fail on a light background."""
    try:
        from PIL import Image
    except ImportError:
        rep.note("Pillow not installed -- skipped the dark-background check on figure files")
        return

    checked = 0
    for fid, fig in sorted(reg.items()):
        page = fig.get("page", "")
        hits = list((ASSETS / page).glob(f"{fid}_*")) if (ASSETS / page).exists() else []
        for f in hits:
            if f.suffix.lower() not in {".png", ".webp", ".jpg", ".jpeg", ".gif"}:
                continue
            try:
                im = Image.open(f).convert("RGB")
            except Exception as exc:
                rep.warn(str(f.relative_to(ROOT)), f"could not be opened: {exc}")
                continue
            w, h = im.size
            corners = [im.getpixel(p) for p in
                       ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
            mean = tuple(sum(c[i] for c in corners) / 4 for i in range(3))
            if any(abs(mean[i] - SURFACE_RGB[i]) > SURFACE_TOLERANCE for i in range(3)):
                rep.error(str(f.relative_to(ROOT)),
                          f"background is {tuple(round(v) for v in mean)}, not the dark "
                          f"surface {SURFACE_RGB}. Light-theme figures are regenerated, "
                          f"not recoloured")
            checked += 1
    rep.note(f"checked the background of {checked} figure file(s)")


def check_page_figures(body: str, fm: dict, reg: dict, path: Path, rep: Report) -> set[str]:
    """Every figure a page shows must be registered, and registered to that page."""
    used = set()
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body):
        m = re.search(r"(F\d+\.\d+)", target)
        if not m:
            rep.error(path.name, f"image '{target}' has no figure id in its filename "
                                 f"(expected something like F05.3_name.webp)")
            continue
        fid = m.group(1)
        used.add(fid)
        if fid not in reg:
            rep.error(path.name, f"figure '{fid}' is not registered in experiments/figures.yaml")
        elif reg[fid].get("page") != fm.get("id"):
            rep.error(path.name, f"figure '{fid}' is registered to page "
                                 f"'{reg[fid].get('page')}', not '{fm.get('id')}'")
    for target in re.findall(r"!\[([^\]]*)\]\([^)]+\)", body):
        if not target.strip():
            rep.error(path.name, "an image has empty alt text")

    # A page that ships with a broken image is the silent failure this whole
    # structure exists to prevent, so the file has to be on disk.
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body):
        f = (path.parent / target).resolve()
        if not f.exists():
            rep.error(path.name, f"image file does not exist: {target}")

    # Links to sibling pages that have not been written yet.
    for target in re.findall(r"\]\((\d\d-[a-z0-9-]+\.md)[^)]*\)", body):
        if not (path.parent / target).exists():
            rep.error(path.name, f"links to '{target}', which does not exist yet")
    return used


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", help="validate one page id only")
    ap.add_argument("--strict", action="store_true", help="warnings fail the run")
    args = ap.parse_args()

    rep = Report()
    reg = load_registry(rep)
    check_registry(reg, rep)
    check_figure_files(reg, rep)

    pages = sorted(p for p in NOTEBOOK.glob("*.md")
                   if not p.name.startswith("_") and p.name != "AUTHORING.md")
    if args.page:
        pages = [p for p in pages if p.stem == args.page]
        if not pages:
            print(f"no page with id '{args.page}'")
            return 1
    if not pages:
        rep.warn("notebook/", "no pages found")

    all_claims: list[tuple[str, dict]] = []
    used_figures: set[str] = set()

    for path in pages:
        text = path.read_text(encoding="utf-8")
        fm, body = split_front_matter(text, path, rep)
        if fm is None:
            continue
        check_front_matter(fm, path, rep)
        for c in check_claims(fm, body, path, rep):
            all_claims.append((path.stem, c))
        check_sections(body, path, rep)
        check_opening_block(body, path, rep)
        check_repro_against_data(fm, body, path, rep)
        check_render_count(fm, body, rep, path)
        check_header_corpus(fm, body, path, rep)
        check_reproducibility(body, path, rep)
        check_duplicate_columns(body, path, rep)
        check_language(body, path, rep)
        check_cadence(body, path, rep)
        used_figures |= check_page_figures(body, fm, reg, path, rep)

    ids = [c["id"] for _, c in all_claims if c.get("id")]
    for cid in {i for i in ids if ids.count(i) > 1}:
        rep.error("claims", f"claim id '{cid}' is used on more than one page")

    for fid, fig in reg.items():
        if fid not in used_figures and fig.get("page") in {p.stem for p in pages}:
            rep.warn(f"figures.yaml[{fid}]", "registered but not referenced by its page")

    print(f"\n  {len(pages)} page(s) · {len(all_claims)} claim(s) · "
          f"{len(reg)} registered figure(s)\n")
    for n in rep.notes:
        print(f"  NOTE  {n}")
    for w in rep.warns:
        print(f"  WARN  {w}")
    for e in rep.errors:
        print(f"  ERROR {e}")

    failed = bool(rep.errors) or (args.strict and bool(rep.warns))
    print(f"\n  {'FAIL' if failed else 'PASS'} -- "
          f"{len(rep.errors)} error(s), {len(rep.warns)} warning(s)\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
