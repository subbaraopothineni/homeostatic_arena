#!/usr/bin/env bash
# Train every pre-registered v0.2 run in parallel, one CPU thread each
# (docs/preregistration_v0.2.md, section 4). Usage, from the repository root:
#   PY=python bash experiments/train_all.sh
set -euo pipefail
PY=${PY:-python}
OUT=${OUT:-results/v02/models}
mkdir -p "$OUT"
RUNS="FULL:0 FULL:1 FULL:2 FULL:3 FULL:4 NOEFF:0 NOEFF:1 NOEFF:2 NOFWD:0 NOFWD:1 NOFWD:2
      UNTRAINED:0 UNTRAINED:1 UNTRAINED:2 UNTRAINED:3 UNTRAINED:4"
for spec in $RUNS; do
  v=${spec%%:*}; s=${spec##*:}
  "$PY" -m experiments.train_agent --variant "$v" --seed "$s" --out "$OUT" \
      > "$OUT/${v}_seed${s}.log" 2>&1 &
done
wait
echo "all runs finished"
