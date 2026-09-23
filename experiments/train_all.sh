#!/usr/bin/env bash
# Train every pre-registered run in parallel, one CPU thread each.
#   Study 2  (docs/preregistration_v0.2.md):  PY=python bash experiments/train_all.sh
#   Study 2b (docs/preregistration_v0.2b.md): WORLD=agency_b OUT=results/v02b/models bash experiments/train_all.sh
#   Study 1b (docs/preregistration_v0.2b.md): WORLD=study1 OUT=results/study1b/models RUNS="FULL:0 FULL:1 FULL:2 FULL:3 FULL:4" bash experiments/train_all.sh
set -euo pipefail
PY=${PY:-python}
WORLD=${WORLD:-agency}
OUT=${OUT:-results/v02/models}
RUNS=${RUNS:-"FULL:0 FULL:1 FULL:2 FULL:3 FULL:4 NOEFF:0 NOEFF:1 NOEFF:2 NOFWD:0 NOFWD:1 NOFWD:2
      UNTRAINED:0 UNTRAINED:1 UNTRAINED:2 UNTRAINED:3 UNTRAINED:4"}
mkdir -p "$OUT"
for spec in $RUNS; do
  v=${spec%%:*}; s=${spec##*:}
  "$PY" -m experiments.train_agent --variant "$v" --seed "$s" --world "$WORLD" --out "$OUT" \
      > "$OUT/${v}_seed${s}.log" 2>&1 &
done
wait
echo "all runs finished"
