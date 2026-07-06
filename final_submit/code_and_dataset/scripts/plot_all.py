# file: scripts/plot_all.py
"""一键生成所有图表到 figures/。"""
import os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
OUT_DIR = os.path.join(ROOT, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

REWARDS = ["baseline", "balanced", "comfort", "aggressive", "conservative"]

scripts_to_run = []

# 1. 训练曲线（baseline + balanced）
for r in ["baseline", "balanced"]:
    scripts_to_run.append(["python", os.path.join(SCRIPTS, "plot_curves.py"),
                           "--reward", r, "--out-dir", OUT_DIR])

# 2. Seed 方差图（baseline + balanced + comfort）
for r in ["baseline", "balanced", "comfort"]:
    scripts_to_run.append(["python", os.path.join(SCRIPTS, "plot_seeds.py"),
                           "--reward", r, "--out-dir", OUT_DIR])

# 3. Reward 分量图
for algo in ["dqn", "ppo"]:
    scripts_to_run.append(["python", os.path.join(SCRIPTS, "plot_reward.py"),
                           "--algo", algo, "--out-dir", OUT_DIR])

generated = []
for cmd in scripts_to_run:
    print(f"[plot_all] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                                cwd=ROOT)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"[plot_all] ERROR: {e}")

for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    size_kb = os.path.getsize(fpath) / 1024
    generated.append(f"  {f} ({size_kb:.1f} KB)")

print(f"\n{'='*50}")
print(f"Generated {len(generated)} figures:")
for g in generated:
    print(g)
print(f"{'='*50}")
