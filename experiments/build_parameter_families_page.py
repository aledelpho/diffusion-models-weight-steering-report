# -*- coding: utf-8 -*-
"""
experiments/build_parameter_families_page.py (superseded)
============================================
A local page for reading `benchmark_parameter_families` by eye: every preset of every live family,
laid out from its most negative dose to its most positive, with a notes field under each.

    python experiments/build_parameter_families_page.py (superseded)

Writes `presets.html` and `_thumbs/` into the bench folder. It scans `renders/` and `archive_d100/`
rather than trusting a plan, so the ladder it shows is the one that exists on disk. The thumbnails
are for navigation only; clicking one opens the real PNG at 1:1.

The analyst's own reading of these renders is deliberately NOT in the page. Alessandro is being
asked what he sees; telling him first is how an observer gets anchored.

No render is generated.
"""
from __future__ import annotations

# Superseded by experiments/build_annotation_page.py, which builds the same page for any bench.
# Kept as an entry point so anything pointing here still works; it does not duplicate the builder.
import runpy
import sys

if __name__ == "__main__":
    sys.argv = ["build_annotation_page.py", "parameter_families"]
    runpy.run_path(str(__file__.rsplit("/", 1)[0].rsplit("\\", 1)[0] + "/build_annotation_page.py"),
                   run_name="__main__")
