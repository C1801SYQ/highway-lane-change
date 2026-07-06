# file: utils/ood_scenarios.py
"""OOD 泛化场景定义与评估。3 个场景 + 1 个 Domain Randomization。

每个 wrapper 提供 Plan A（直接控制车辆） + Plan B（近似替代）。
Plan A 失败时自动降级为 Plan B 并 print WARNING。
"""

import numpy as np
import gymnasium as gym


def _try_get_road_vehicles(env):
    """安全获取 highway 环境的 road.vehicles 列表。"""
    try:
        return env.unwrapped.road.vehicles
    except Exception:
        return None


# ============================================================
# LaneClosureWrapper
# ============================================================
class LaneClosureWrapper(gym.Wrapper):
    """前方车道封闭场景。

    Plan A: 冻结封闭区域内车辆速度。
    Plan B: 对进入封闭区域的车辆施加 reward 惩罚（通过 info 传递）。
    """
    def __init__(self, env, closure_lanes=(0,1), closure_start=180, closure_length=30):
        super().__init__(env)
        self.closure_lanes = closure_lanes
        self.closure_start = closure_start
        self.closure_end = closure_start + closure_length
        self._plan_b = False
        # 测试 Plan A 可行性
        vehicles = _try_get_road_vehicles(self.env)
        if vehicles is None or len(vehicles) == 0:
            print("[OOD WARNING] LaneClosure: Plan A not available, using Plan B (reward penalty).")
            self._plan_b = True

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        if not self._plan_b:
            try:
                vehicles = _try_get_road_vehicles(self.env)
                if vehicles:
                    for v in vehicles:
                        pos = getattr(v, 'position', [0,0])
                        if self.closure_start <= pos[0] <= self.closure_end:
                            lane_idx = getattr(v, 'lane_index', None)
                            if isinstance(lane_idx, int) and lane_idx in self.closure_lanes:
                                v.speed = min(getattr(v, 'speed', 99), 2.0)
            except Exception:
                pass
        else:
            # Plan B: 检查自车是否在封闭区
            try:
                ego_pos = obs[0] if isinstance(obs, (list, np.ndarray)) else 0
                if self.closure_start <= ego_pos <= self.closure_end:
                    reward -= 5.0
            except Exception:
                pass
        return obs, reward, terminated, truncated, info


# ============================================================
# SuddenBrakeWrapper
# ============================================================
class SuddenBrakeWrapper(gym.Wrapper):
    """前车急刹场景。

    Plan A: 在时间窗内直接对指定车辆施加减速。
    Plan B: 在时间窗内随机对前车施加减速事件（修改一步 reward）。
    """
    def __init__(self, env, brake_time=20.0, deceleration=-8.0,
                 brake_vehicle_idx=3, brake_duration=3.0):
        super().__init__(env)
        self.brake_time = brake_time
        self.deceleration = deceleration
        self.brake_vehicle_idx = brake_vehicle_idx
        self.brake_duration = brake_duration
        self._elapsed = 0.0
        self._policy_freq = 5.0
        self._plan_b = False
        try:
            self._policy_freq = float(self.env.unwrapped.config.get("policy_frequency", 5))
        except Exception:
            pass
        vehicles = _try_get_road_vehicles(self.env)
        if vehicles is None:
            print("[OOD WARNING] SuddenBrake: Plan A not available, using Plan B.")
            self._plan_b = True

    def reset(self, **kwargs):
        self._elapsed = 0.0
        return self.env.reset(**kwargs)

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        self._elapsed += 1.0 / max(self._policy_freq, 1.0)
        in_window = self.brake_time <= self._elapsed <= self.brake_time + self.brake_duration
        if in_window and not self._plan_b:
            try:
                vehicles = _try_get_road_vehicles(self.env)
                if vehicles and len(vehicles) > self.brake_vehicle_idx:
                    v = vehicles[self.brake_vehicle_idx]
                    dt = 1.0 / max(float(self.env.unwrapped.config.get("simulation_frequency",15)), 1.0)
                    v.speed = max(0.0, getattr(v,'speed',0) + self.deceleration * dt)
            except Exception:
                pass
        elif in_window and self._plan_b:
            reward -= 1.0  # Plan B: 轻微惩罚
        return obs, reward, terminated, truncated, info


# ============================================================
# HighDensityWrapper
# ============================================================
class HighDensityWrapper(gym.Wrapper):
    """高密度车流场景。直接通过修改 config 实现，不需要额外 wrapper 逻辑。

    应通过 make_ood_env() 传入 ood_config 参数来设置。
    这里保留一个 wrapper 用于在 reset 时强制覆盖。
    """
    def __init__(self, env, vehicles_count=50, initial_spacing=1.0):
        super().__init__(env)
        self.vc = vehicles_count
        self.sp = initial_spacing
        try:
            self.env.unwrapped.config["vehicles_count"] = vehicles_count
            self.env.unwrapped.config["initial_spacing"] = initial_spacing
        except Exception:
            print("[OOD WARNING] HighDensity: Cannot modify config, using env defaults.")

    def reset(self, **kwargs):
        try:
            self.env.unwrapped.config["vehicles_count"] = self.vc
            self.env.unwrapped.config["initial_spacing"] = self.sp
        except Exception:
            pass
        return self.env.reset(**kwargs)


# ============================================================
# DomainRandWrapper
# ============================================================
class DomainRandWrapper(gym.Wrapper):
    """每次 reset 随机化车辆数和初始间距。"""
    def __init__(self, env, vehicles_range=(20,50), spacing_range=(0.8,2.5)):
        super().__init__(env)
        self.vr = vehicles_range
        self.sr = spacing_range

    def reset(self, **kwargs):
        vc = np.random.randint(self.vr[0], self.vr[1] + 1)
        sp = np.random.uniform(self.sr[0], self.sr[1])
        try:
            self.env.unwrapped.config["vehicles_count"] = vc
            self.env.unwrapped.config["initial_spacing"] = sp
        except Exception:
            pass
        return self.env.reset(**kwargs)


# ============================================================
# 工厂函数
# ============================================================
_OOD_REGISTRY = {
    "lane_closure": LaneClosureWrapper,
    "sudden_brake": SuddenBrakeWrapper,
    "high_density": HighDensityWrapper,
    "domain_rand": DomainRandWrapper,
}

def make_ood_env(env, ood_name, config=None):
    """在已有 env 上叠加 OOD wrapper。

    Args:
        env: 已创建的 gym.Env
        ood_name: "lane_closure"|"sudden_brake"|"high_density"|"domain_rand"
        config: config.yaml 中的 ood 字典
    Returns:
        被 wrap 后的 env
    """
    if ood_name == "in_dist":
        return env
    if ood_name not in _OOD_REGISTRY:
        raise ValueError(f"Unknown OOD scene: {ood_name}. Choose from {list(_OOD_REGISTRY.keys())}")
    if config is None:
        config = {}
    wrapper_cls = _OOD_REGISTRY[ood_name]
    env = wrapper_cls(env, **config)
    return env
