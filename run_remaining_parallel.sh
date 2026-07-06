#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

ALGOS=("dqn" "ppo")
REWARDS=("baseline" "comfort" "aggressive" "balanced" "conservative")
SEEDS=(42 123 456 789 1024)

JOBS=${JOBS:-4}

mkdir -p run_logs/parallel

echo "=== Resume parallel training ==="
echo "Concurrency: $JOBS"
echo ""

for algo in "${ALGOS[@]}"; do
  for reward in "${REWARDS[@]}"; do
    for seed in "${SEEDS[@]}"; do

      run_dir="logs/${algo}/${reward}/seed_${seed}"
      metric_file="${run_dir}/final_metrics.json"

      if [ -f "$metric_file" ]; then
        echo "[SKIP] $algo / $reward / seed=$seed already done"
        continue
      fi

      echo "[RUN ] $algo / $reward / seed=$seed"

      python "train_${algo}.py" --reward "$reward" --seed "$seed" \
        > "run_logs/parallel/${algo}_${reward}_seed${seed}.log" 2>&1 &

      while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do
        sleep 5
      done

    done
  done
done

wait
echo "=== ALL REMAINING TRAINING DONE ==="
