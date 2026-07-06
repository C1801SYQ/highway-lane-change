# file: eval.py
"""独立评估脚本。用法:
    python eval.py --algo dqn --reward balanced --seed 42 --scene in_dist --n-episodes 20
    python eval.py --algo ppo --reward balanced --seed 42 --scene all
    python eval.py --algo dqn --reward balanced --seed 42 --scene lane_closure --render
"""
import argparse, yaml, os, sys, json
import numpy as np

def _load_cfg():
    root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _load_model(algo, reward_cfg, seed, log_dir, custom_path=None):
    """加载 best_model.zip（优先）或 final_model.zip。"""
    if custom_path and os.path.exists(custom_path):
        p = custom_path
    else:
        run_dir = os.path.join(log_dir, algo, reward_cfg, f"seed_{seed}")
        p = os.path.join(run_dir, "best_model.zip")
        if not os.path.exists(p):
            p = os.path.join(run_dir, "final_model.zip")
    if not os.path.exists(p):
        raise FileNotFoundError(f"No model found. Run training first. Tried: {p}")
    if algo == "dqn":
        from stable_baselines3 import DQN
        return DQN.load(p)
    else:
        from stable_baselines3 import PPO
        return PPO.load(p)


def _run_episode(model, env, record_frames=False):
    """跑一个 episode，返回 (reward, crashed, speeds_mean, lane_changes, accel_total, frames, action_counts)。"""
    obs, _ = env.reset()
    done = False
    ep_r = 0.0
    speeds = []
    crashed = False
    lc_count = 0
    accel_total = 0.0
    action_counts = [0, 0, 0, 0, 0]  # LANE_LEFT, IDLE, LANE_RIGHT, FASTER, SLOWER
    frames = []
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        # SB3 predict 返回的 action 可能是 0-d/1-d numpy array 或标量
        action_int = int(action.item()) if hasattr(action, "item") else int(action)
        if 0 <= action_int < 5:
            action_counts[action_int] += 1
        _step_out = env.step(action)
        if len(_step_out) == 5:
            obs, rew, terminated, truncated, info = _step_out
            done = bool(terminated) or bool(truncated)
        else:
            obs, rew, done, info = _step_out
            done = bool(done)
        ep_r += float(rew)
        # info
        if isinstance(info, (list, tuple)):
            info = info[0] if len(info) > 0 else {}
        if not isinstance(info, dict):
            info = {}
        speeds.append(float(info.get("speed", 0)))
        if info.get("crashed", False):
            crashed = True
        if int(action) in (0, 2):
            lc_count += 1
        if int(action) in (3, 4):
            accel_total += 1
        if record_frames:
            try:
                frame = env.render()
                if frame is not None:
                    frames.append(frame)
            except Exception:
                pass
    avg_spd = float(np.mean(speeds)) if speeds else 0.0
    return ep_r, crashed, avg_spd, lc_count, accel_total, frames, action_counts


def _save_video_frames(frames, out_dir, scene_name):
    """保存帧：优先 ffmpeg 合成 mp4，fallback 保存 PNG 序列。"""
    os.makedirs(out_dir, exist_ok=True)
    if not frames:
        print("[WARNING] No frames captured.")
        return
    # 尝试 ffmpeg
    import subprocess, tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        for i, frm in enumerate(frames):
            import cv2
            cv2.imwrite(os.path.join(tmpdir, f"frm_{i:05d}.png"),
                        cv2.cvtColor(frm, cv2.COLOR_RGB2BGR))
    except ImportError:
        from PIL import Image
        for i, frm in enumerate(frames):
            img = Image.fromarray(frm)
            img.save(os.path.join(tmpdir, f"frm_{i:05d}.png"))
    mp4_path = os.path.join(out_dir, f"{scene_name}.mp4")
    # ffmpeg
    try:
        subprocess.run(["ffmpeg", "-y", "-framerate", "15", "-i",
                        os.path.join(tmpdir, "frm_%05d.png"), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", mp4_path], check=True, capture_output=True)
        print(f"[Video] Saved to {mp4_path}")
    except Exception:
        png_dir = os.path.join(out_dir, f"{scene_name}_frames")
        os.makedirs(png_dir, exist_ok=True)
        import shutil
        for f in os.listdir(tmpdir):
            shutil.copy(os.path.join(tmpdir, f), os.path.join(png_dir, f))
        print(f"[Video] ffmpeg not available, saved PNG frames to {png_dir}")
    # 清理临时
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, required=True, choices=["dqn","ppo"])
    parser.add_argument("--reward", type=str, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--scene", type=str, default="in_dist",
                        choices=["in_dist","lane_closure","sudden_brake","high_density","all"])
    parser.add_argument("--n-episodes", type=int, default=20)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--model-path", type=str, default=None)
    args = parser.parse_args()

    cfg = _load_cfg()
    log_dir = cfg["training"]["log_dir"]
    video_dir = cfg["training"].get("video_dir", "./videos")

    # 加载 reward 权重
    rw_cfg = cfg["reward"].get(args.reward, cfg["reward"]["baseline"])
    reward_weights = {k: v for k, v in rw_cfg.items() if k.startswith("w_")}

    # 加载模型
    from utils.logging import seed_everything
    seed_everything(args.seed)
    model = _load_model(args.algo, args.reward, args.seed, log_dir, args.model_path)

    # OOD 场景列表
    if args.scene == "all":
        scenes = ["in_dist","lane_closure","sudden_brake","high_density"]
    else:
        scenes = [args.scene]

    # 加载 OOD 配置
    ood_cfg_map = cfg.get("ood", {})

    all_results = {}
    for scene in scenes:
        print(f"\n{'='*50}")
        print(f"[Eval] algo={args.algo} reward={args.reward} seed={args.seed} scene={scene}")
        print(f"{'='*50}")

        # 创建环境
        from make_env import make_env as _make_env_single
        env, _ = _make_env_single(
            render_mode="rgb_array" if args.render else None,
            seed=args.seed + 99999,
            reward_weights=reward_weights,
            ood_name=scene if scene != "in_dist" else None,
            record_video=False,
        )

        ep_results = []
        hacking_records = []
        for ep_idx in range(args.n_episodes):
            ep_r, crashed, avg_spd, lc_count, accel_total, frames, action_counts = _run_episode(
                model, env, record_frames=(args.render and ep_idx == 0 and scene == "in_dist"))
            ep_results.append(dict(ep=ep_idx, reward=round(ep_r,2), collision=crashed,
                                   speed=round(avg_spd,2), lane_changes=lc_count,
                                   accel_total=accel_total))
            hacking_records.append(dict(speed=avg_spd, lane_changes=lc_count,
                                        collision=crashed, length=40,
                                        action_counts=action_counts))
            print(f"  Ep {ep_idx:3d}: R={ep_r:7.1f} spd={avg_spd:5.1f} "
                  f"lc={lc_count:2d} crash={'YES' if crashed else 'no'}")

            if args.render and ep_idx == 0 and frames:
                os.makedirs(video_dir, exist_ok=True)
                _save_video_frames(frames, video_dir, f"{args.algo}_{args.reward}_{scene}")

        env.close()

        # 汇总指标
        rwds = [e["reward"] for e in ep_results]
        cr = sum(1 for e in ep_results if e["collision"]) / len(ep_results)
        avg_spd = float(np.mean([e["speed"] for e in ep_results]))
        avg_lc = float(np.mean([e["lane_changes"] for e in ep_results]))
        sr = sum(1 for e in ep_results if not e["collision"]) / len(ep_results)

        summary = dict(scene=scene, algo=args.algo, reward_cfg=args.reward, seed=args.seed,
                       n_episodes=args.n_episodes, collision_rate=round(cr,4),
                       mean_speed=round(avg_spd,2), mean_lc=round(avg_lc,2),
                       success_rate=round(sr,4), mean_reward=round(float(np.mean(rwds)),2),
                       std_reward=round(float(np.std(rwds)),2))
        all_results[scene] = summary

        # Reward hacking 检测
        from utils.reward import detect_reward_hacking
        hacking_report = detect_reward_hacking(hacking_records)
        n_warn = len(hacking_report.get("warnings", []))
        if n_warn > 0:
            print(f"\n[WARNING] Reward Hacking detected in scene={scene}: {n_warn} flags")
            for w in hacking_report["warnings"]:
                print(f"  - {w}")
            hpath = os.path.join(log_dir, args.algo, args.reward, f"seed_{args.seed}",
                                 f"hacking_report_{scene}.json")
            os.makedirs(os.path.dirname(hpath), exist_ok=True)
            with open(hpath, "w", encoding="utf-8") as f:
                json.dump(hacking_report, f, indent=2)
            print(f"  → Report saved to {hpath}")

        print(f"  => CR={cr:.3f} Spd={avg_spd:.1f} LC={avg_lc:.1f} SR={sr:.3f} "
              f"R={summary['mean_reward']:.1f}±{summary['std_reward']:.1f}")

    # 保存汇总 JSON
    eval_dir = os.path.join(log_dir, args.algo, args.reward, f"seed_{args.seed}")
    os.makedirs(eval_dir, exist_ok=True)
    spath = os.path.join(eval_dir, f"eval_{args.scene}.json")
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[Eval] Summary saved to {spath}")


if __name__ == "__main__":
    main()
