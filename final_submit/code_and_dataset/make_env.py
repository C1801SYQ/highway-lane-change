# file: make_env.py
"""环境工厂。支持 GrayscaleImage→OccupancyGrid 自动 fallback，兼容 gymnasium 版本差异。"""
import os, sys
import gymnasium as gym
from gymnasium.wrappers import FrameStackObservation
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import numpy as np
import highway_env

# 注册 highway-env 环境
try:
    highway_env.register_highway_envs()
except Exception:
    pass  # 可能已注册


def _load_config():
    """加载 config.yaml（相对于项目根目录）。"""
    import yaml
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, "config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_env_config(ood_name=None):
    """组装 highway-env 环境配置字典。"""
    cfg = _load_config()
    ec = cfg["env"]
    env_cfg = {
        "lanes_count": ec["lanes_count"],
        "vehicles_count": ec["vehicles_count"],
        "duration": ec["duration"],
        "initial_spacing": ec["initial_spacing"],
        "simulation_frequency": ec["simulation_frequency"],
        "policy_frequency": ec["policy_frequency"],
        "offroad_terminal": ec["offroad_terminal"],
        "collision_reward": ec["collision_reward"],
        "right_lane_reward": ec["right_lane_reward"],
        "high_speed_reward": ec["high_speed_reward"],
        "lane_change_reward": ec["lane_change_reward"],
        "normalize_reward": ec["normalize_reward"],
        "action": {"type": cfg["action"]["type"]},
    }
    # 观测（优先 GrayscaleImage）
    obs_cfg = cfg["observation"]
    env_cfg["observation"] = {
        "type": obs_cfg["primary"],
    }
    # OOD 覆盖
    if ood_name and ood_name != "in_dist":
        ood_cfg = cfg.get("ood", {}).get(ood_name, {})
        for k in ["vehicles_count", "initial_spacing", "duration"]:
            if k in ood_cfg:
                env_cfg[k] = ood_cfg[k]
    return env_cfg


class _CustomRewardWrapper(gym.Wrapper):
    """用自定义 reward 完全替换环境内置奖励。"""
    def __init__(self, env, calculator):
        super().__init__(env)
        self.calc = calculator

    def step(self, action):
        obs, _reward, terminated, truncated, info = self.env.step(action)
        total, components = self.calc.compute_detailed(obs, int(action), info)
        # 写入 info 供日志
        if not isinstance(info, dict):
            info = {}
        info["reward_components"] = components
        info["reward_total"] = total
        return obs, total, terminated, truncated, info


def make_env(render_mode=None, seed=None, reward_weights=None, ood_name=None,
             record_video=False, video_dir=None):
    """创建单个 highway 环境（GrayscaleImage 优先，失败 fallback OccupancyGrid）。"""
    env_id = _load_config()["env"]["id"]
    obs_cfg = _load_config()["observation"]
    env_cfg = _get_env_config(ood_name)

    # 创建环境
    mk_kwargs = {"id": env_id}
    if render_mode:
        mk_kwargs["render_mode"] = render_mode
    else:
        mk_kwargs["render_mode"] = None
    env = gym.make(**mk_kwargs)

    # 配置
    try:
        env.unwrapped.configure(env_cfg)
    except Exception as e:
        print(f"[WARNING] env.configure() failed: {e}, using defaults")

    # 尝试 GrayscaleImage，失败则 fallback
    use_grayscale = True
    try:
        _reset_out = env.reset()
        if isinstance(_reset_out, tuple):
            test_obs = _reset_out[0]
        else:
            test_obs = _reset_out
        if isinstance(test_obs, np.ndarray):
            _ = test_obs.shape
    except Exception:
        use_grayscale = False

    if not use_grayscale:
        print("[WARNING] GrayscaleImage not available, falling back to OccupancyGrid.")
        env_cfg["observation"] = {
            "type": obs_cfg["fallback"],
            "features": obs_cfg.get("fallback_features", ["presence", "vx", "vy"]),
        }
        try:
            env.unwrapped.configure(env_cfg)
        except Exception:
            pass
        env = gym.make(**mk_kwargs)
        try:
            env.unwrapped.configure(env_cfg)
        except Exception:
            pass

    # FrameStack（GrayscaleImage 需要 4 帧堆叠）
    if use_grayscale:
        try:
            env = FrameStackObservation(env, stack_size=obs_cfg["stack_size"])
        except Exception as e:
            print(f"[WARNING] FrameStack failed: {e}, continuing without stacking")

    # 自定义 reward
    if reward_weights:
        from utils.reward import RewardCalculator
        spd_cfg = _load_config().get("speed_reward", {})
        calc = RewardCalculator(
            reward_weights,
            speed_target=spd_cfg.get("target", 25.0),
            speed_sigma=spd_cfg.get("sigma", 8.0),
        )
        env = _CustomRewardWrapper(env, calc)

    # OOD wrapper（必须在 Monitor 之前，确保 reward 已替换）
    if ood_name and ood_name != "in_dist":
        from utils.ood_scenarios import make_ood_env as _make_ood
        ood_params = _load_config().get("ood", {}).get(ood_name, {})
        env = _make_ood(env, ood_name, ood_params)

    # Monitor
    env = Monitor(env)

    # 录像（双策略）
    if record_video:
        vdir = video_dir or _load_config()["training"].get("video_dir", "./videos")
        _setup_recording(env, vdir)

    # Seed
    if seed is not None:
        env.reset(seed=seed)
        try:
            env.action_space.seed(seed)
        except Exception:
            pass

    return env, use_grayscale


def _setup_recording(env, video_dir):
    """录像：优先 gymnasium RecordVideo，失败回退逐帧保存。"""
    os.makedirs(video_dir, exist_ok=True)
    try:
        from gymnasium.wrappers import RecordVideo
        env = RecordVideo(env, video_dir, episode_trigger=lambda ep: True)
        return env
    except Exception:
        print("[WARNING] RecordVideo failed, will save PNG frames on next eval call.")
    return env


def make_vec_env(n_envs=1, seed=None, reward_weights=None, ood_name=None,
                 use_vec_normalize=True, vec_normalize_path=None):
    """创建 VecEnv（用于 SB3 训练/评估）。"""
    def _init():
        e, _use_gs = make_env(seed=seed, reward_weights=reward_weights, ood_name=ood_name)
        return e

    vec_env = DummyVecEnv([_init] * n_envs)
    if use_vec_normalize and vec_normalize_path and os.path.exists(vec_normalize_path):
        try:
            vec_env = VecNormalize.load(vec_normalize_path, vec_env)
        except Exception:
            vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, clip_obs=10.0)
    elif use_vec_normalize:
        vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, clip_obs=10.0)
    return vec_env
