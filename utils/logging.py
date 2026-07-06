# file: utils/logging.py
"""训练日志与评估结果保存（CSV + JSON），保证中途 crash 不丢数据。"""
import os, csv, json, time
import numpy as np

def make_run_dir(log_dir, algo, reward_cfg, seed):
    run_dir = os.path.join(log_dir, algo, reward_cfg, f"seed_{seed}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

class CSVLogger:
    """逐行写入 CSV，每次 flush 保证 crash-safe。"""
    def __init__(self, path, columns):
        self.path = path
        self.columns = columns
        os.makedirs(os.path.dirname(path), exist_ok=True)
        existed = os.path.exists(path)
        self.f = open(path, "a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.f)
        if not existed:
            self.writer.writerow(columns)
            self.f.flush()
    def log(self, **kwargs):
        row = [kwargs.get(c, "") for c in self.columns]
        self.writer.writerow(row)
        self.f.flush()
    def close(self):
        self.f.close()

# ============================================================
# 评估回调
# ============================================================
class EvalCallback:
    """
    替代 SB3 EvalCallback。
    每 eval_freq 步在独立 eval_env 上评估，写入 CSV。

    防呆:
      - 自动关闭 VecNormalize 训练模式
      - deterministic=True
      - 记录 episode 级指标供后续分析
    """
    def __init__(self, eval_env, run_dir, eval_freq=5000, n_eval_episodes=10,
                 best_metric="mean_reward", verbose=1):
        self.eval_env = eval_env
        self.run_dir = run_dir
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.best_metric = best_metric
        self.best_value = -float("inf")
        self.best_sr = -float("inf")  # 最佳成功率单独追踪
        self.num_timesteps = 0
        self.verbose = verbose
        # 汇总 CSV
        self.summary_csv = CSVLogger(
            os.path.join(run_dir, "eval_metrics.csv"),
            ["timestep","mean_reward","std_reward","collision_rate",
             "avg_speed","avg_lane_changes","avg_accel_penalty","success_rate","n_episodes"]
        )
        # 逐 episode CSV
        self.ep_csv = CSVLogger(
            os.path.join(run_dir, "eval_episodes.csv"),
            ["timestep","ep_idx","reward","collision","speed","lane_changes","accel_total"]
        )
        # reward components CSV（每个 episode 各分量的平均值）
        self.comp_csv = CSVLogger(
            os.path.join(run_dir, "eval_reward_components.csv"),
            ["timestep","ep_idx","collision","speed","lane_change","accel","right_lane","total"]
        )

    def __call__(self, _locals, _globals):
        self.num_timesteps = _locals["self"].num_timesteps
        # 只在 eval_freq 的倍数执行评估
        if self.num_timesteps % self.eval_freq != 0:
            return True
        model = _locals["self"]
        # 关闭 VecNormalize 训练模式
        _set_eval_mode(self.eval_env, False)

        ep_rewards = []
        ep_infos = []
        for ep_i in range(self.n_eval_episodes):
            _reset_out = self.eval_env.reset()
            if isinstance(_reset_out, tuple):
                obs, _extra = _reset_out
            else:
                obs = _reset_out
            done = False
            ep_r = 0.0
            speeds = []
            crashed = False
            lc_count = 0
            accel_total = 0.0
            # reward components 累加
            comp_sums = {
                "collision": 0.0,
                "speed": 0.0,
                "lane_change": 0.0,
                "accel": 0.0,
                "right_lane": 0.0,
            }
            n_steps = 0
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                # 统计 action 类型：0=LANE_LEFT, 1=IDLE, 2=LANE_RIGHT, 3=FASTER, 4=SLOWER
                action_int = int(action.item()) if hasattr(action, "item") else int(action)
                if action_int in (0, 2):
                    lc_count += 1
                if action_int in (3, 4):
                    accel_total += 1
                _step_out = self.eval_env.step(action)
                # 兼容 gymnasium 新旧 API：5元组(obs,rew,term,trunc,info) vs 4元组(obs,rew,done,info)
                if len(_step_out) == 5:
                    obs, rew, terminated, truncated, info = _step_out
                    done = bool(terminated) or bool(truncated)
                else:
                    obs, rew, done, info = _step_out
                    done = bool(done)
                ep_r += float(rew)
                _info = _unwrap_info(info)
                speeds.append(float(_info.get("speed", 0)))
                if _info.get("crashed", False):
                    crashed = True
                # 累加 reward components
                components = _info.get("reward_components", {})
                for k in comp_sums:
                    comp_sums[k] += float(components.get(k, 0.0))
                n_steps += 1
            ep_rewards.append(ep_r)
            ep_infos.append({
                "collision": crashed,
                "speed": float(np.mean(speeds)) if speeds else 0.0,
                "lane_changes": lc_count,
                "accel_total": accel_total,
            })
            self.ep_csv.log(
                timestep=self.num_timesteps, ep_idx=ep_i,
                reward=round(ep_r,2), collision=int(crashed),
                speed=round(ep_infos[-1]["speed"],2),
                lane_changes=lc_count, accel_total=round(accel_total,4),
            )
            # 写入 reward components 平均值
            if n_steps > 0:
                comp_mean = {k: round(comp_sums[k] / n_steps, 4) for k in comp_sums}
                comp_total = round(sum(comp_mean.values()), 4)
            else:
                comp_mean = {k: 0.0 for k in comp_sums}
                comp_total = 0.0
            self.comp_csv.log(
                timestep=self.num_timesteps, ep_idx=ep_i,
                collision=comp_mean["collision"],
                speed=comp_mean["speed"],
                lane_change=comp_mean["lane_change"],
                accel=comp_mean["accel"],
                right_lane=comp_mean["right_lane"],
                total=comp_total,
            )

        # 汇总指标
        n = len(ep_infos)
        collisions = sum(1 for x in ep_infos if x["collision"])
        cr = round(collisions/n, 4) if n else 0.0
        avg_spd = round(float(np.mean([x["speed"] for x in ep_infos])), 2) if n else 0.0
        avg_lc = round(float(np.mean([x["lane_changes"] for x in ep_infos])), 2) if n else 0.0
        avg_acc = round(float(np.mean([x["accel_total"] for x in ep_infos])), 4) if n else 0.0
        sr = round(sum(1 for x in ep_infos if not x["collision"])/n, 4) if n else 0.0
        mean_r = round(float(np.mean(ep_rewards)), 2)
        std_r = round(float(np.std(ep_rewards)), 2)

        self.summary_csv.log(
            timestep=self.num_timesteps, mean_reward=mean_r, std_reward=std_r,
            collision_rate=cr, avg_speed=avg_spd, avg_lane_changes=avg_lc,
            avg_accel_penalty=avg_acc, success_rate=sr, n_episodes=n,
        )

        # 保存最佳模型
        cur_val = mean_r if self.best_metric == "mean_reward" else sr
        if cur_val > self.best_value:
            self.best_value = cur_val
            model.save(os.path.join(self.run_dir, "best_model.zip"))
            if self.verbose:
                print(f"[Eval @{self.num_timesteps}] NEW BEST {self.best_metric}={cur_val:.3f}")
        # 同时追踪最佳成功率
        if sr > self.best_sr:
            self.best_sr = sr

        # 恢复训练模式
        _set_eval_mode(self.eval_env, True)

        if self.verbose:
            print(f"[Eval @{self.num_timesteps}] R={mean_r:.1f}±{std_r:.1f} "
                  f"CR={cr:.3f} Spd={avg_spd:.1f} LC={avg_lc:.1f} SR={sr:.3f}")
        return True

def _set_eval_mode(vec_env, training):
    """安全切换 VecNormalize 训练/评估模式。"""
    try:
        env = vec_env
        if hasattr(env, "venv"):
            env = env.venv
        if hasattr(env, "training"):
            env.training = training
        if hasattr(env, "norm_reward"):
            env.norm_reward = training
    except Exception:
        pass

def _unwrap_info(info):
    """兼容 VecEnv 返回的 info 可能是 list/dict。"""
    if isinstance(info, (list, tuple)):
        return info[0] if len(info) > 0 else {}
    return info if isinstance(info, dict) else {}

def seed_everything(seed):
    """固定所有随机源。"""
    import random
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

def save_config_snapshot(run_dir, config_dict):
    """保存训练时的配置快照，确保可追溯。"""
    import yaml
    path = os.path.join(run_dir, "config_snapshot.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False)

def save_final_json(run_dir, summary):
    """保存最终汇总 JSON。"""
    import json
    path = os.path.join(run_dir, "final_metrics.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
