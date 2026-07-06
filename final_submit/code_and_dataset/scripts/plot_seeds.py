# file: scripts/plot_seeds.py
"""Seed 方差箱线图：collision_rate / speed / lc_freq 按 algo+reward 分组。"""
import os, sys, json, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

COLORS = {"dqn": "#1F4E79", "ppo": "#C0392B"}

def load_seed_data(log_dir, algo, reward_cfg, seeds):
    """加载所有 seed 的 final_metrics.json，返回 {metric: [values]}。"""
    metrics = {"collision_rate": [], "mean_speed": [], "mean_lc": [], "success_rate": [], "mean_reward": []}
    for s in seeds:
        jp = os.path.join(log_dir, algo, reward_cfg, f"seed_{s}", "final_metrics.json")
        if not os.path.exists(jp):
            # fallback: eval_metrics.csv 最后一行
            cp = os.path.join(log_dir, algo, reward_cfg, f"seed_{s}", "eval_metrics.csv")
            if not os.path.exists(cp):
                continue
            with open(cp, encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) < 2:
                continue
            last = lines[-1].strip().split(",")
            if len(last) >= 8:
                metrics["collision_rate"].append(float(last[3]))
                metrics["mean_speed"].append(float(last[4]))
                metrics["mean_lc"].append(float(last[5]))
                metrics["success_rate"].append(float(last[7]))
                metrics["mean_reward"].append(float(last[1]))
            continue
        try:
            with open(jp, encoding="utf-8") as f:
                jd = json.load(f)
        except Exception:
            continue
        # 从 final_metrics 恢复（字段名略有不同）
        metrics["collision_rate"].append(jd.get("collision_rate", jd.get("best_cr", float("nan"))))
        metrics["mean_speed"].append(jd.get("avg_speed", jd.get("best_speed", float("nan"))))
        metrics["mean_reward"].append(jd.get("best_mean_reward", float("nan")))
        metrics["success_rate"].append(jd.get("success_rate", jd.get("best_sr", float("nan"))))
        metrics["mean_lc"].append(jd.get("avg_lane_changes", jd.get("best_lc", float("nan"))))
    return {k: np.array(v) for k, v in metrics.items() if len(v) > 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reward", type=str, default="balanced")
    parser.add_argument("--log-dir", type=str, default=os.path.join(ROOT, "logs"))
    parser.add_argument("--out-dir", type=str, default=os.path.join(ROOT, "figures"))
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    seeds = [42, 123, 456, 789, 1024]

    dqn_data = load_seed_data(args.log_dir, "dqn", args.reward, seeds)
    ppo_data = load_seed_data(args.log_dir, "ppo", args.reward, seeds)

    metric_names = {
        "collision_rate": "Collision Rate",
        "mean_speed": "Avg Speed (m/s)",
        "mean_reward": "Mean Reward",
        "success_rate": "Success Rate",
    }

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()
    for idx, (key, label) in enumerate(metric_names.items()):
        ax = axes[idx]
        data_to_plot = []
        positions = []
        labels_list = []
        if key in dqn_data and len(dqn_data[key]) > 0:
            data_to_plot.append(dqn_data[key])
            positions.append(1)
            labels_list.append("DQN")
        if key in ppo_data and len(ppo_data[key]) > 0:
            data_to_plot.append(ppo_data[key])
            positions.append(2)
            labels_list.append("PPO")
        if data_to_plot:
            bp = ax.boxplot(data_to_plot, positions=positions, labels=labels_list,
                            patch_artist=True, widths=0.5)
            for patch, pos in zip(bp["boxes"], positions):
                c = COLORS.get(["dqn","ppo"][pos-1], "#888888")
                patch.set_facecolor(c)
                patch.set_alpha(0.3)
        ax.set_title(label)
        ax.grid(True, alpha=0.3)
    fig.suptitle(f"Seed Variance: DQN vs PPO ({args.reward} reward)", fontsize=14)
    fig.tight_layout()
    out = os.path.join(args.out_dir, f"seed_variance_{args.reward}.png")
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[plot_seeds] Saved: {out}")


if __name__ == "__main__":
    main()
