# file: select_best.py
"""自动选最优 seed 的模型。用法:
    python select_best.py --algo dqn --reward balanced
    python select_best.py --algo ppo --reward balanced --metric success_rate
"""
import argparse, os, json, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, required=True, choices=["dqn","ppo"])
    parser.add_argument("--reward", type=str, required=True)
    parser.add_argument("--metric", type=str, default="mean_reward",
                        choices=["mean_reward","success_rate"])
    parser.add_argument("--log-dir", type=str, default="./logs")
    args = parser.parse_args()

    base = os.path.join(args.log_dir, args.algo, args.reward)
    if not os.path.isdir(base):
        print(f"[ERROR] No results found at {base}")
        sys.exit(1)

    best_seed = None
    best_val = -float("inf")
    best_path = None
    results = []

    for entry in sorted(os.listdir(base)):
        d = os.path.join(base, entry)
        if not os.path.isdir(d) or not entry.startswith("seed_"):
            continue
        seed_str = entry.replace("seed_", "")
        try:
            seed = int(seed_str)
        except ValueError:
            continue

        # 优先读 final_metrics.json
        jp = os.path.join(d, "final_metrics.json")
        val = None
        if os.path.exists(jp):
            try:
                with open(jp, encoding="utf-8") as f:
                    jd = json.load(f)
                if args.metric == "success_rate":
                    # 优先 success_rate，其次 best_sr
                    val = jd.get("success_rate", None)
                    if val is None:
                        val = jd.get("best_sr", None)
                elif args.metric == "mean_reward":
                    # 优先 best_mean_reward，其次 mean_reward
                    val = jd.get("best_mean_reward", None)
                    if val is None:
                        val = jd.get("mean_reward", None)
            except Exception:
                val = None
        # fallback: 读 eval_metrics.csv 最后一行
        if val is None:
            cp = os.path.join(d, "eval_metrics.csv")
            if os.path.exists(cp):
                try:
                    with open(cp, encoding="utf-8") as f:
                        lines = f.readlines()
                    if len(lines) > 1:
                        last = lines[-1].strip().split(",")
                        # columns: timestep,mean_reward,std_reward,collision_rate,avg_speed,
                        #          avg_lane_changes,avg_accel_penalty,success_rate,n_episodes
                        if args.metric == "success_rate" and len(last) > 7:
                            val = float(last[7])  # success_rate 在第 7 列(0-indexed)
                        elif len(last) > 1:
                            val = float(last[1])  # mean_reward 在第 1 列
                except Exception:
                    val = None
        if val is None:
            results.append(dict(seed=seed, value=None, model_path=None))
            continue

        mp = os.path.join(d, "best_model.zip")
        if not os.path.exists(mp):
            mp = os.path.join(d, "final_model.zip")
        results.append(dict(seed=seed, value=round(val,4), model_path=mp))
        if val > best_val:
            best_val = val
            best_seed = seed
            best_path = mp

    # 排序输出
    results.sort(key=lambda x: x.get("value") or -float("inf"), reverse=True)

    print(f"\n{'='*60}")
    print(f"Best Model Selection: {args.algo}/{args.reward}  (metric={args.metric})")
    print(f"{'='*60}")
    print(f"{'Rank':<6} {'Seed':<8} {'Value':<12} {'Path'}")
    print(f"{'-'*60}")
    for rank, r in enumerate(results):
        flag = " ← BEST" if r["seed"] == best_seed else ""
        print(f"{rank+1:<6} {r['seed']:<8} {r.get('value','N/A'):<12} {r.get('model_path','N/A')}{flag}")

    # 保存
    out = {
        "algo": args.algo, "reward_cfg": args.reward,
        "metric": args.metric, "best_seed": best_seed,
        "best_value": best_val, "best_model_path": best_path,
        "all_results": results,
    }
    opath = os.path.join(base, "best_selection.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {opath}")

    # 返回 best model path 供后续使用
    if best_path:
        print(f"\n[BEST] seed={best_seed} value={best_val} model={best_path}")


if __name__ == "__main__":
    main()
