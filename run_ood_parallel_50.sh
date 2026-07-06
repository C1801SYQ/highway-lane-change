#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

ALGOS=("dqn" "ppo")
REWARDS=("baseline" "comfort" "aggressive" "balanced" "conservative")

JOBS=${JOBS:-10}
EPISODES=${EPISODES:-50}

mkdir -p run_logs/ood_parallel

echo "=== Parallel OOD Evaluation ==="
echo "Concurrency: $JOBS"
echo "Episodes per scene: $EPISODES"
echo ""

for algo in "${ALGOS[@]}"; do
  for reward in "${REWARDS[@]}"; do

    if find "logs/${algo}/${reward}" -name "eval_all.json" | grep -q .; then
      echo "[SKIP] $algo / $reward already evaluated"
      continue
    fi

    seed=$(python - <<PY
import json
with open("logs/$algo/$reward/best_selection.json", "r", encoding="utf-8") as f:
    d = json.load(f)
print(d["best_seed"])
PY
)

    echo "[RUN ] $algo / $reward / seed=$seed"

    python eval.py \
      --algo "$algo" \
      --reward "$reward" \
      --seed "$seed" \
      --scene all \
      --n-episodes "$EPISODES" \
      > "run_logs/ood_parallel/${algo}_${reward}_seed${seed}.log" 2>&1 &

    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do
      sleep 3
    done

  done
done

wait
echo "=== ALL OOD EVALUATION DONE ==="
