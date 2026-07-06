# file: scripts/plot_reward.py
"""Reward 分量贡献图：不同 reward 配置下各分量均值对比。

读取 logs/{algo}/{reward}/seed_*/eval_reward_components.csv，
聚合后生成分组柱状图保存到 figures/reward_components_{algo}.png。
"""
import os, sys, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

COMPONENT_KEYS = ["collision", "speed", "lane_change", "accel", "right_lane"]
COMPONENT_COLORS = ["#C0392B", "#27AE60", "#2980B9", "#F39C12", "#8E44AD"]
COMPONENT_LABELS = ["Collision", "Speed", "Lane Change", "Accel", "Right Lane"]

REWARD_CFGS = ["baseline", "comfort", "aggressive", "balanced", "conservative"]
SEEDS = [42, 123, 456, 789, 1024]


def load_components(log_dir, algo, reward_cfg):
    """读取某个 algo+reward 下所有 seed 的 reward components，返回各分量跨 episode 均值。"""
    comp_all = {k: [] for k in COMPONENT_KEYS}
    found_any = False
    for s in SEEDS:
        cp = os.path.join(log_dir, algo, reward_cfg, f"seed_{s}", "eval_reward_components.csv")
        if not os.path.exists(cp):
            continue
        try:
            with open(cp, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            continue
        if len(lines) < 2:
            continue
        # 解析 CSV（header: timestep,ep_idx,collision,speed,lane_change,accel,right_lane,total）
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) < 8:
                continue
            try:
                comp_all["collision"].append(float(parts[2]))
                comp_all["speed"].append(float(parts[3]))
                comp_all["lane_change"].append(float(parts[4]))
                comp_all["accel"].append(float(parts[5]))
                comp_all["right_lane"].append(float(parts[6]))
                found_any = True
            except (ValueError, IndexError):
                continue
    if not found_any:
        return None
    return {k: np.mean(comp_all[k]) for k in COMPONENT_KEYS}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, default="dqn", choices=["dqn", "ppo"])
    parser.add_argument("--log-dir", type=str, default=os.path.join(ROOT, "logs"))
    parser.add_argument("--out-dir", type=str, default=os.path.join(ROOT, "figures"))
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # 加载所有 reward 配置的数据
    data = {}
    for rc in REWARD_CFGS:
        comps = load_components(args.log_dir, args.algo, rc)
        if comps is not None:
            data[rc] = comps
        else:
            print(f"[WARNING] No reward component data for {args.algo}/{rc}, skipping.")

    if not data:
        # 无数据时生成占位图
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5,
                "No reward component data found.\n"
                "Run training with EvalCallback to generate eval_reward_components.csv files.",
                transform=ax.transAxes, ha="center", va="center", fontsize=14, color="gray")
        ax.set_title(f"Reward Components ({args.algo.upper()}) — No Data")
        out = os.path.join(args.out_dir, f"reward_components_{args.algo}.png")
        fig.savefig(out, dpi=200)
        plt.close(fig)
        print(f"[plot_reward] Placeholder (no data) saved: {out}")
        return

    # 绘制分组柱状图
    reward_labels = list(data.keys())
    n_rewards = len(reward_labels)
    n_comps = len(COMPONENT_KEYS)
    x = np.arange(n_rewards)
    bar_width = 0.15

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (key, color, label) in enumerate(zip(COMPONENT_KEYS, COMPONENT_COLORS, COMPONENT_LABELS)):
        values = [data[rc][key] for rc in reward_labels]
        offset = (i - n_comps / 2 + 0.5) * bar_width
        ax.bar(x + offset, values, bar_width, color=color, alpha=0.85, label=label, edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([rc.capitalize() for rc in reward_labels], fontsize=11)
    ax.set_ylabel("Mean Reward Component Value", fontsize=12)
    ax.set_title(f"Reward Component Contributions — {args.algo.upper()}", fontsize=14)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(y=0, color="black", linewidth=0.8)
    fig.tight_layout()

    out = os.path.join(args.out_dir, f"reward_components_{args.algo}.png")
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"[plot_reward] Saved: {out}")
    print(f"[plot_reward] Processed {len(data)} reward configs for {args.algo.upper()}.")


if __name__ == "__main__":
    main()
