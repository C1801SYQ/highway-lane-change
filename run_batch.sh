#!/bin/bash
# file: run_batch.sh
# 批量训练脚本 (Linux/macOS)
# 用法:
#   bash run_batch.sh                 # 完整矩阵 50 次
#   bash run_batch.sh --quick         # 快速模式: 2 algo × 2 reward × 3 seeds = 12次
#   bash run_batch.sh --jobs 4        # 限制并发数

set -e
cd "$(dirname "$0")"

ALGOS=("dqn" "ppo")
REWARDS_FULL=("baseline" "comfort" "aggressive" "balanced" "conservative")
REWARDS_QUICK=("baseline" "balanced")
SEEDS_FULL=(42 123 456 789 1024)
SEEDS_QUICK=(42 123 456)

QUICK=false
JOBS=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick) QUICK=true; shift ;;
        --jobs) JOBS="$2"; shift 2 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

if $QUICK; then
    REWARDS=("${REWARDS_QUICK[@]}")
    SEEDS=("${SEEDS_QUICK[@]}")
    echo "=== QUICK MODE: ${#ALGOS[@]} algo × ${#REWARDS[@]} reward × ${#SEEDS[@]} seeds ==="
else
    REWARDS=("${REWARDS_FULL[@]}")
    SEEDS=("${SEEDS_FULL[@]}")
    echo "=== FULL MODE: ${#ALGOS[@]} algo × ${#REWARDS[@]} reward × ${#SEEDS[@]} seeds ==="
fi

TOTAL=$((${#ALGOS[@]} * ${#REWARDS[@]} * ${#SEEDS[@]}))
echo "Total experiments: $TOTAL"
echo "Concurrency: $JOBS"
echo ""

mkdir -p logs models figures
SUMMARY="logs/summary.csv"
echo "algo,reward,seed,best_mean_reward,status" > "$SUMMARY"

COUNT=0
for algo in "${ALGOS[@]}"; do
  for reward in "${REWARDS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      COUNT=$((COUNT + 1))
      echo "[$COUNT/$TOTAL] $algo / $reward / seed=$seed"

      if [ "$JOBS" -gt 1 ]; then
        python "train_${algo}.py" --reward "$reward" --seed "$seed" &
        # 控制并发
        while [ "$(jobs -r | wc -l)" -ge "$JOBS" ]; do
          sleep 2
        done
      else
        python "train_${algo}.py" --reward "$reward" --seed "$seed"
      fi

      # 提取 best_mean_reward 写入 summary
      BEST_VAL=""
      JSON_PATH="logs/${algo}/${reward}/seed_${seed}/final_metrics.json"
      if [ -f "$JSON_PATH" ]; then
        BEST_VAL=$(python -c "import json; d=json.load(open('$JSON_PATH')); print(d.get('best_mean_reward',''))" 2>/dev/null || echo "")
      fi
      echo "$algo,$reward,$seed,$BEST_VAL,done" >> "$SUMMARY"
      echo ""
    done
  done
done

# 等待后台任务完成
wait

echo "=== BATCH DONE ==="
echo "Summary: $SUMMARY"
python select_best.py --algo dqn --reward balanced
python select_best.py --algo ppo --reward balanced
