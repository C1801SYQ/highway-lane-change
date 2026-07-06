# file: scripts/plot_curves.py
"""训练曲线：DQN vs PPO，mean±std shading。"""
import os, sys, json, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

COLORS = {"dqn": "#1F4E79", "ppo": "#C0392B"}

def load_curves(log_dir, algo, reward_cfg, seeds):
    """从 logs/ 加载所有 seed 的 eval_metrics.csv，返回 timesteps(N,), rewards(S,N)."""
    all_ts = None
    all_rwds = []
    for s in seeds:
        cp = os.path.join(log_dir, algo, reward_cfg, f"seed_{s}", "eval_metrics.csv")
        if not os.path.exists(cp):
            continue
        ts, rwds = [], []
        with open(cp, encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            ts.append(int(parts[0]))
            rwds.append(float(parts[1]))
        if all_ts is None:
            all_ts = np.array(ts)
        all_rwds.append(np.array(rwds))
    if all_ts is None or len(all_rwds) == 0:
        return None, None
    # 对齐到最小长度
    min_len = min(len(r) for r in all_rwds)
    all_ts = all_ts[:min_len]
    stacked = np.array([r[:min_len] for r in all_rwds])
    return all_ts, stacked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reward", type=str, default="balanced")
    parser.add_argument("--log-dir", type=str, default=os.path.join(ROOT, "logs"))
    parser.add_argument("--out-dir", type=str, default=os.path.join(ROOT, "figures"))
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    seeds = [42, 123, 456, 789, 1024]

    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ["dqn", "ppo"]:
        ts, rwds = load_curves(args.log_dir, algo, args.reward, seeds)
        if ts is None:
            print(f"[WARNING] No data for {algo}/{args.reward}")
            continue
        mu = np.mean(rwds, axis=0)
        std = np.std(rwds, axis=0)
        c = COLORS[algo]
        ax.plot(ts, mu, color=c, linewidth=2, label=f"{algo.upper()}")
        ax.fill_between(ts, mu-std, mu+std, color=c, alpha=0.15)

    ax.set_xlabel("Timesteps")
    ax.set_ylabel("Episode Reward")
    ax.set_title(f"Training Curves: DQN vs PPO ({args.reward} reward)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = os.path.join(args.out_dir, f"training_curves_{args.reward}.png")
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[plot_curves] Saved: {out}")


if __name__ == "__main__":
    main()
