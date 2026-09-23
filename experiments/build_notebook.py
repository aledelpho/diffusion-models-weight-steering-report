#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_notebook.py -- notebook/*.md is the source; README table and index.html are output.

Two documents with the same content and a hand-maintained correspondence between them will
drift: that is how this repository ended up with a section numbered 4.5 in one place and 12.4
in the other. So the index table and the GitHub Pages site are generated, and editing either
by hand is a mistake the next build silently reverts.

    python experiments/build_notebook.py            # write README table + index.html
    python experiments/build_notebook.py --check    # fail if either is out of date (for CI)

The README table is written between these markers, which must already exist in README.md:

    <!-- CLAIMS:BEGIN -->
    <!-- CLAIMS:END -->

Dependencies: PyYAML, Markdown.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("build_notebook.py needs PyYAML:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebook"
README = ROOT / "README.md"
INDEX = ROOT / "index.html"

BEGIN, END = "<!-- CLAIMS:BEGIN -->", "<!-- CLAIMS:END -->"

# Status colours are the reserved status palette, and they never carry meaning alone:
# every one ships with its word. "open" is deliberately NOT a status colour -- an open
# question is not an outcome.
STATUS = {
    "holds":      ("Holds",      "#0ca30c"),
    "ambiguous":  ("Ambiguous",  "#fab219"),
    "overturned": ("Overturned", "#d03b3b"),
    "open":       ("Open",       "#898781"),
}
ORDER = ["holds", "ambiguous", "overturned", "open"]

SURFACE, INK, INK_2, MUTED, GRID = "#1a1a19", "#ffffff", "#c3c2b7", "#898781", "#2c2c2a"


def read_pages() -> list[dict]:
    pages = []
    for path in sorted(NOTEBOOK.glob("*.md")):
        if path.name.startswith("_") or path.name == "AUTHORING.md":
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        fm = yaml.safe_load(text[3:end]) or {}
        fm["_body"] = text[end + 4:]
        fm["_path"] = path
        pages.append(fm)
    return pages


def claims_table(pages: list[dict]) -> str:
    rows = []
    for page in pages:
        for c in page.get("claims") or []:
            rows.append((c.get("status", "open"), c, page))
    rows.sort(key=lambda r: (ORDER.index(r[0]) if r[0] in ORDER else 9,
                             r[2].get("id", ""), r[1].get("id", "")))

    out = [BEGIN,
           "",
           "| | What | What it rests on |",
           "|---|---|---|"]
    for status, c, page in rows:
        label, _ = STATUS.get(status, ("Open", MUTED))
        stmt = " ".join((c.get("statement") or "").split())
        ev = " ".join((c.get("evidence") or "").split())
        link = f"notebook/{page['id']}.md{c.get('anchor', '')}"
        out.append(f"| **{label}** | [{stmt}]({link}) | {ev} |")
    out += ["", END]
    return "\n".join(out)


def render_index(pages: list[dict]) -> str:
    try:
        import markdown
    except ImportError:
        sys.exit("build_notebook.py needs Markdown for index.html:  pip install markdown")

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "attr_list"])

    nav, body = [], []
    for page in pages:
        # un id che comincia con una cifra e' HTML valido ma non e' un
        # selettore CSS valido: querySelector("#05-...") solleva
        pid = "p-" + page["id"]
        label, colour = STATUS.get(page.get("status", "open"), ("Open", MUTED))
        nav.append(f'<li><a href="#{pid}"><span class="dot" style="background:{colour}"></span>'
                   f'{html.escape(page.get("title", pid))}</a></li>')
        md.reset()
        # Rewrite the relative links the markdown files use between themselves.
        src = re.sub(r"\]\((?:\.\./)?(?:notebook/)?(\d\d-[a-z0-9-]+)\.md(#[a-z0-9-]*)?\)",
                     r"](#p-\1\2)", page["_body"])
        src = src.replace("](../assets/", "](assets/").replace("](../docs/", "](docs/")
        src = src.replace("](../README.md#what-holds-and-what-does-not)", "](#claims)")
        # il blocco di stato in testa alla pagina serve su GitHub, dove non c'e'
        # la barra generata; qui sarebbe la stessa riga due volte
        src = re.sub(r"^# .+\n+(> .*\n)+", lambda m: m.group(0).split("\n")[0] + "\n\n",
                     src, count=1, flags=re.M)
        html_body = md.convert(src)
        # I titoli di pagine diverse producono gli stessi slug ("The data",
        # "The verdict"...). In un documento unico collidono, quindi ogni id e
        # ogni ancora interna si prefissano con la pagina.
        html_body = re.sub(r'id="([^"]+)"', rf'id="{pid}--\1"', html_body)
        html_body = re.sub(r'href="#([^"]+)"', rf'href="#{pid}--\1"', html_body)
        # il rimando all'indice e' l'unica ancora che esce dalla pagina
        html_body = html_body.replace(f'href="#{pid}--claims"', 'href="#claims"')
        html_body = html_body.replace("<table>", '<div class="tablewrap"><table>')\
                             .replace("</table>", "</table></div>")
        body.append(
            f'<section id="{pid}">\n'
            f'<p class="status"><span class="pill" style="--c:{colour}">{label}</span>'
            f'<span class="corpus">{html.escape(corpus_line(page))}</span></p>\n'
            f'{html_body}\n</section>')

    rows = []
    for page in pages:
        for c in page.get("claims") or []:
            rows.append((c.get("status", "open"), c, page))
    rows.sort(key=lambda r: (ORDER.index(r[0]) if r[0] in ORDER else 9, r[2]["id"]))
    claim_rows = "\n".join(
        f'<tr><td><span class="pill" style="--c:{STATUS.get(s, ("", MUTED))[1]}">'
        f'{STATUS.get(s, ("Open", ""))[0]}</span></td>'
        f'<td><a href="#{_claim_target(p, c)}">'
        f'{html.escape(" ".join((c.get("statement") or "").split()))}</a></td>'
        f'<td class="ev">{html.escape(" ".join((c.get("evidence") or "").split()))}</td></tr>'
        for s, c, p in rows)

    return TEMPLATE.format(surface=SURFACE, ink=INK, ink2=INK_2, muted=MUTED, grid=GRID,
                           nav="\n".join(nav), claims=claim_rows, body="\n".join(body))


def _claim_target(page, claim):
    """Nel documento unico una claim punta al proprio titolo, non alla pagina:
    due cancelletti in un href non sono un'ancora."""
    pid = "p-" + page["id"]
    anchor = (claim.get("anchor") or "").lstrip("#")
    return f"{pid}--{anchor}" if anchor else pid


def corpus_line(page: dict) -> str:
    c = page.get("corpus") or {}
    bits = []
    if c.get("renders"):
        bits.append(f"{c['renders']} renders")
    if c.get("prompts"):
        bits.append(f"{c['prompts']} prompts")
    if c.get("seeds"):
        bits.append(f"{len(c['seeds'])} seeds")
    if page.get("preregistration"):
        bits.append("pre-registered")
    if page.get("date"):
        bits.append(str(page["date"]))
    return " · ".join(bits)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weight-Space Steering in Diffusion Models — Lab Notebook</title>
<meta name="description" content="A public lab notebook on steering diffusion models through small, structured weight edits.">
<!-- GENERATED by experiments/build_notebook.py from notebook/*.md — do not edit by hand. -->
<style>
  :root {{
    --surface: {surface}; --ink: {ink}; --ink-2: {ink2}; --muted: {muted}; --grid: {grid};
    --measure: 40rem;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0; background: var(--surface); color: var(--ink);
    font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: grid; grid-template-columns: 17rem 1fr; gap: 0;
  }}
  nav {{
    position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto;
    padding: 2rem 1.25rem; border-right: 1px solid var(--grid);
  }}
  nav h2 {{ font-size: .7rem; letter-spacing: .1em; text-transform: uppercase;
            color: var(--muted); margin: 0 0 .75rem; }}
  nav ul {{ list-style: none; margin: 0 0 1.75rem; padding: 0; }}
  nav a {{ display: flex; gap: .55rem; align-items: baseline; padding: .3rem 0;
           color: var(--ink-2); text-decoration: none; font-size: .9rem; }}
  nav a:hover {{ color: var(--ink); }}
  .dot {{ width: .5rem; height: .5rem; border-radius: 50%; flex: none; }}
  main {{ padding: 3rem 2rem 6rem; max-width: calc(var(--measure) + 4rem); min-width: 0; }}
  h1 {{ font-size: 2rem; line-height: 1.2; margin: 0 0 .5rem; }}
  h2 {{ font-size: 1.35rem; margin: 2.5rem 0 .75rem; }}
  h3 {{ font-size: 1.05rem; margin: 2rem 0 .5rem; color: var(--ink-2); }}
  h4 {{ font-size: .95rem; margin: 1.5rem 0 .5rem; color: var(--ink-2); }}
  p, li {{ max-width: var(--measure); }}
  a {{ color: #3987e5; }}
  section {{ border-top: 1px solid var(--grid); padding-top: 2rem; margin-top: 2.25rem; }}
  section:first-of-type {{ border-top: 0; }}
  .status {{ display: flex; gap: .75rem; align-items: center; flex-wrap: wrap; margin: 0 0 1rem; }}
  .pill {{ display: inline-block; padding: .12rem .5rem; border-radius: 999px;
           font-size: .72rem; font-weight: 600; letter-spacing: .02em;
           color: var(--c); border: 1px solid var(--c); white-space: nowrap; }}
  .corpus {{ color: var(--muted); font-size: .82rem; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 1.5rem 0;
         border: 1px solid var(--grid); border-radius: 4px; background: var(--surface); }}
  table {{ border-collapse: collapse; margin: 1.25rem 0; font-size: .9rem; width: 100%; }}
  th, td {{ border-bottom: 1px solid var(--grid); padding: .5rem .6rem;
            text-align: left; vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; font-size: .78rem;
        text-transform: uppercase; letter-spacing: .05em; }}
  td.ev {{ color: var(--ink-2); font-size: .85rem; }}
  #claims td a {{ color: var(--ink); text-decoration: none;
                  border-bottom: 1px solid var(--grid); }}
  #claims td a:hover {{ border-bottom-color: var(--muted); }}
  code {{ background: #232320; padding: .1rem .35rem; border-radius: 3px; font-size: .86em; }}
  pre {{ background: #232320; padding: 1rem; border-radius: 6px; overflow-x: auto;
         border: 1px solid var(--grid); }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ margin: 1.25rem 0; padding: .5rem 0 .5rem 1.1rem;
                border-left: 2px solid var(--grid); color: var(--ink-2); }}
  .tablewrap {{ overflow-x: auto; margin: 1.25rem 0; }}
  .tablewrap table {{ margin: 0; min-width: 32rem; }}
  @media (max-width: 60rem) {{
    body {{ grid-template-columns: 1fr; }}
    nav {{ position: static; height: auto; border-right: 0;
           border-bottom: 1px solid var(--grid); }}
    main {{ padding: 2rem 1rem 4rem; max-width: 100%; }}
    /* The claims table is the page's index: it stacks into cards rather than
       scrolling sideways, because a reader must be able to skim it on a phone. */
    #claims table, #claims thead, #claims tbody, #claims tr, #claims td {{ display: block; }}
    #claims thead {{ display: none; }}
    #claims tr {{ border-bottom: 1px solid var(--grid); padding: .9rem 0; }}
    #claims td {{ border: 0; padding: .15rem 0; }}
    #claims td.ev::before {{ content: "Rests on — "; color: var(--muted); }}
  }}
</style>
</head>
<body>
<nav>
  <h2>Experiments</h2>
  <ul>
{nav}
  </ul>
  <h2>Elsewhere</h2>
  <ul>
    <li><a href="#claims">What holds, what does not</a></li>
    <li><a href="docs/scope.md">Scope and ladder</a></li>
    <li><a href="docs/errors_log.md">The pitfalls checklist</a></li>
    <li><a href="data/">Measurement files</a></li>
  </ul>
</nav>
<main>
  <h1>Weight-Space Steering in Diffusion Models</h1>
  <p class="corpus">A public lab notebook. Every number on this page comes from a file in
     <code>data/</code>, and every figure is built by a script that reads one.</p>

  <section id="claims">
    <h2>What holds, and what does not</h2>
    <table>
      <thead><tr><th></th><th>Claim</th><th>What it rests on</th></tr></thead>
      <tbody>
{claims}
      </tbody>
    </table>
  </section>

{body}
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if the outputs are out of date instead of writing them")
    args = ap.parse_args()

    pages = read_pages()
    if not pages:
        print("no pages found under notebook/")
        return 1

    table = claims_table(pages)
    index = render_index(pages)
    stale = []

    if README.exists():
        text = README.read_text(encoding="utf-8")
        if BEGIN in text and END in text:
            new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), table, text, flags=re.S)
            if new != text:
                stale.append("README.md")
                if not args.check:
                    README.write_text(new, encoding="utf-8")
        else:
            print(f"  NOTE  README.md has no {BEGIN} / {END} markers; table not inserted")
            print("\n" + table + "\n")
    else:
        print("  NOTE  no README.md yet; the table is printed below\n")
        print(table + "\n")

    if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != index:
        stale.append("index.html")
        if not args.check:
            INDEX.write_text(index, encoding="utf-8")

    n_claims = sum(len(p.get("claims") or []) for p in pages)
    if args.check:
        if stale:
            print(f"\n  OUT OF DATE: {', '.join(stale)} — run experiments/build_notebook.py\n")
            return 1
        print(f"\n  up to date · {len(pages)} page(s) · {n_claims} claim(s)\n")
        return 0

    print(f"\n  built · {len(pages)} page(s) · {n_claims} claim(s) · "
          f"{'wrote ' + ', '.join(stale) if stale else 'nothing changed'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
