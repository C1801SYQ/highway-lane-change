# file: utils/reward.py
"""自定义奖励函数 + Reward Hacking 检测。"""
import math

class RewardCalculator:
    """根据权重配置计算 step 总奖励及各分量值。"""
    def __init__(self, weights: dict, speed_target=25.0, speed_sigma=8.0):
        self.w = weights
        self.speed_target = speed_target
        self.speed_sigma = speed_sigma
        self._prev_speed = None

    def _extract_speed(self, obs, info):
        """优先从 info["speed"] 读取速度，其次 obs["speed"]，否则 0.0。

        highway-env 默认 GrayscaleImage 观测下 obs 是 numpy 数组而非 dict，
        因此速度必须通过 info 传递。此方法保证兼容多种观测类型。
        """
        if isinstance(info, dict) and "speed" in info:
            return float(info.get("speed", 0.0))
        if isinstance(obs, dict) and "speed" in obs:
            return float(obs.get("speed", 0.0))
        return 0.0

    def compute_detailed(self, obs, action, info, prev_speed=None):
        """
        返回 (total, components_dict)。
        速度奖励: 高斯型 exp(-(v-target)^2 / (2*sigma^2))
        """
        speed = self._extract_speed(obs, info)
        crashed = bool(info.get("crashed", False)) if isinstance(info, dict) else False

        # 碰撞
        c_collision = abs(self.w.get("w_collision", 10.0)) * (-1.0 if crashed else 0.0)
        # 速度（高斯型）
        diff = speed - self.speed_target
        c_speed = self.w.get("w_high_speed", 0.0) * math.exp(-diff*diff/(2*self.speed_sigma*self.speed_sigma))
        # 变道惩罚
        c_lc = 0.0
        if int(action) in (0, 2):
            c_lc = -abs(self.w.get("w_lane_change", 0.0))
        # 急加速/减速惩罚
        c_accel = 0.0
        if int(action) in (3, 4):
            c_accel = -abs(self.w.get("w_accel_penalty", 0.0))
        # 靠右奖励
        c_right = 0.0
        wr = self.w.get("w_right_lane", 0.0)
        if wr != 0.0 and isinstance(obs, dict):
            x_pos = float(obs.get("x", 0))
            lane_idx = max(0.0, x_pos / 4.0)
            c_right = wr * max(0.0, 1.0 - lane_idx / 4.0)

        components = dict(
            collision=round(c_collision,4), speed=round(c_speed,4),
            lane_change=round(c_lc,4), accel=round(c_accel,4), right_lane=round(c_right,4),
        )
        total = sum(components.values())
        return total, components

    def compute(self, obs, action, info):
        """简化接口，只返回 total。"""
        total, _ = self.compute_detailed(obs, action, info)
        return total


# ============================================================
# Reward Hacking 检测
# ============================================================
def detect_reward_hacking(episode_records, threshold_speed=15.0, threshold_lc_freq=2.0):
    """
    检测三种典型 hacking 模式。
    episode_records: list[dict], 每项需含 avg_speed/collision/n_lane_changes/episode_length/action_counts
    返回 {"warnings": [...], "flags": {"turtle": N, "crazy_lc": N, "idle": N}}
    """
    warnings = []
    flags = {"turtle": 0, "crazy_lc": 0, "idle": 0}
    for i, ep in enumerate(episode_records):
        spd = float(ep.get("speed", 0))
        n_lc = int(ep.get("lane_changes", 0))
        length = max(float(ep.get("length", 40)), 1.0)
        lc_freq = n_lc / max(length, 0.1)
        if spd < threshold_speed and n_lc == 0:
            warnings.append(f"Ep {i}: TURTLE (speed={spd:.1f}<{threshold_speed}, lc=0)")
            flags["turtle"] += 1
        if lc_freq > threshold_lc_freq:
            warnings.append(f"Ep {i}: CRAZY_LC (lc_freq={lc_freq:.2f}>{threshold_lc_freq} Hz)")
            flags["crazy_lc"] += 1
        acts = ep.get("action_counts", [0]*5)
        total_acts = max(sum(acts), 1)
        idle_ratio = acts[1] / total_acts if len(acts) > 1 else 0
        if idle_ratio > 0.95:
            warnings.append(f"Ep {i}: IDLE (ratio={idle_ratio:.3f}>0.95)")
            flags["idle"] += 1
    return {"warnings": warnings, "flags": flags}
