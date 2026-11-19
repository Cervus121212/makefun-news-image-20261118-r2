#!/usr/bin/env python3
"""Entry point for the news-image-20261118 entry (Python 3.13, stdlib only).

The front page is drawn by generate.py (PIL, run at build time) and stored
as entry.png beside this file. This program only copies it to the output
directory the grader provides, so it runs with no network and no
third-party packages. Deterministic: a copy writes the same bytes
every run.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(outdir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
