# file: scripts/plot_final_summary.py
"""Generate final summary comparison figures from final_average_ranking.csv."""

import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

CSV_PATH = os.path.join(ROOT, "run_logs", "final_average_ranking.csv")
OUT_DIR = os.path.join(ROOT, "figures_clean")

# Color palette
PPO_COLOR = "#C0392B"
DQN_COLOR = "#1F4E79"


def load_data() -> pd.DataFrame:
    """Load and lightly prepare the average ranking data."""
    df = pd.read_csv(CSV_PATH)
    # Create a short label for each model
    df["label"] = df["algo"].str.upper() + "-" + df["reward"].str[:4]
    return df.sort_values("avg_rank")


def plot_success_collision(df: pd.DataFrame, out_path: str):
    """Figure: Average Success Rate and Collision Rate (side-by-side bars)."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    labels = df["label"].tolist()
    x = np.arange(len(labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, df["avg_success_rate"].values, width,
                   label="Avg Success Rate", color="#27AE60", edgecolor="white", linewidth=0.5)
    bars2 = ax.bar(x + width/2, df["avg_collision_rate"].values, width,
                   label="Avg Collision Rate", color="#E74C3C", edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Rate", fontsize=11)
    ax.set_title("Average Success Rate and Collision Rate", fontsize=13)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.2)

    # Add value labels on bars
    for bar in bars1:
        h = bar.get_height()
        if h > 0.02:
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.01, f"{h:.3f}",
                    ha="center", va="bottom", fontsize=6.5, rotation=90)
    for bar in bars2:
        h = bar.get_height()
        if h > 0.02:
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.01, f"{h:.3f}",
                    ha="center", va="bottom", fontsize=6.5, rotation=90)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_lc_collision(df: pd.DataFrame, out_path: str):
    """Figure: Average Lane Changes and Collision Rate (dual y-axis)."""
    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    labels = df["label"].tolist()
    x = np.arange(len(labels))
    width = 0.35

    # Collision rate on left y-axis
    color_coll = "#E74C3C"
    bars1 = ax1.bar(x - width/2, df["avg_collision_rate"].values, width,
                    label="Avg Collision Rate", color=color_coll,
                    edgecolor="white", linewidth=0.5)
    ax1.set_ylabel("Collision Rate", fontsize=11, color=color_coll)
    ax1.set_ylim(0, 1.1)
    ax1.tick_params(axis="y", labelcolor=color_coll)
    ax1.grid(axis="y", alpha=0.2)

    # Lane changes on right y-axis
    ax2 = ax1.twinx()
    color_lc = "#2980B9"
    bars2 = ax2.bar(x + width/2, df["avg_mean_lc"].values, width,
                    label="Avg Lane Changes", color=color_lc,
                    edgecolor="white", linewidth=0.5)
    ax2.set_ylabel("Lane Changes / Episode", fontsize=11, color=color_lc)
    ax2.tick_params(axis="y", labelcolor=color_lc)

    # Set x-axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
    ax1.set_title("Average Lane Changes and Collision Rate", fontsize=13)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")

    # Value labels
    for bar in bars1:
        h = bar.get_height()
        if h > 0.02:
            ax1.text(bar.get_x() + bar.get_width()/2., h + 0.01, f"{h:.3f}",
                     ha="center", va="bottom", fontsize=6.5, rotation=90, color=color_coll)
    for bar in bars2:
        h = bar.get_height()
        if h > 1:
            ax2.text(bar.get_x() + bar.get_width()/2., h + 0.3, f"{h:.1f}",
                     ha="center", va="bottom", fontsize=7, rotation=90, color=color_lc)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def main():
    df = load_data()
    print(f"Loaded {len(df)} models from {CSV_PATH}")
    print(df[["label", "avg_success_rate", "avg_collision_rate", "avg_mean_lc", "avg_rank"]].to_string())

    plot_success_collision(df, os.path.join(OUT_DIR, "final_avg_success_collision.png"))
    plot_lc_collision(df, os.path.join(OUT_DIR, "final_lane_change_collision.png"))
    print("\nAll summary figures generated.")


if __name__ == "__main__":
    main()
