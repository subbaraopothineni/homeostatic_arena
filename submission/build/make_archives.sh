#!/usr/bin/env bash
# Rebuild the code-and-data archives in submission/05_code_and_data from the last commit.
# Usage (from anywhere inside the repository): bash submission/build/make_archives.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
out=submission/05_code_and_data
rm -f "$out/homeostatic_arena_code_data.zip" "$out/homeostatic_arena_history.bundle"
git archive --format=zip --prefix=homeostatic_arena/ -o "$out/homeostatic_arena_code_data.zip" HEAD -- \
  agents arena docs experiments results tests README.md requirements.txt requirements-lock.txt pytest.ini \
  submission/build/make_figures.py submission/build/make_archives.sh submission/build/md2docx.js \
  submission/build/build_docs.js submission/build/package.json submission/build/manuscript.md \
  submission/build/cover_letter.md submission/build/supplementary.md
git bundle create "$out/homeostatic_arena_history.bundle" --all
ls -l "$out"
