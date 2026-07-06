# 最终结果分析报告

> 生成时间: 2026-07-07
> 数据来源: run_logs/final_result_summary.csv (40 行, 10 个模型 × 4 场景)

---

## 一、实验设计概述

- 算法: DQN, PPO
- 奖励函数配置: baseline, comfort, aggressive, balanced, conservative
- 训练: 2 × 5 × 5 = 50 组 (5 个随机种子)
- 最优模型: 每 (algo, reward) 组合选出 1 个 best seed, 共 10 个
- OOD 评估场景: in_dist, lane_closure, sudden_brake, high_density
- 评估规模: 10 × 4 = 40 行, 每行 50 episodes

---

## 二、四类场景下的模型表现

### 2.1 In-Distribution 场景

| 排名 | 算法 | Reward | Success | Collision | Reward | Speed | LC |
|------|------|--------|---------|-----------|--------|-------|----|
| 1 | PPO | aggressive | 0.98 | 0.02 | 163.66 | 20.34 | 14.02 |
| 2 | PPO | baseline | 0.90 | 0.10 | 76.37 | 20.66 | 14.30 |
| 3 | PPO | comfort | 0.80 | 0.20 | 66.19 | 21.71 | 0.00 |
| 4 | PPO | balanced | 0.80 | 0.20 | 66.19 | 21.71 | 0.00 |
| 8 | DQN | baseline | 0.06 | 0.94 | 24.04 | 25.35 | 66.50 |
| 9 | DQN | aggressive | 0.02 | 0.98 | 59.42 | 24.96 | 61.78 |
| 10 | DQN | balanced | 0.00 | 1.00 | 4.80 | 29.52 | 0.00 |

**分析**: PPO aggressive 在 in-distribution 场景下表现最佳，成功率 98%，碰撞率仅 2%。DQN 各配置碰撞率均超过 90%，其中 DQN balanced 碰撞率达到 100%。DQN baseline 和 aggressive 出现频繁变道（平均 >60 次/episode），说明策略不稳定。

### 2.2 Lane Closure 场景

车道关闭场景的结果与 in-distribution 场景高度一致。PPO aggressive 仍保持 98% 成功率和 2% 碰撞率。所有模型的 lane_closure 表现与 in_dist 几乎相同，说明车道关闭场景（180-210m 区间封闭两车道）对已学会变道避让的模型影响有限。

### 2.3 Sudden Brake 场景

PPO aggressive 成功率略降至 96%，碰撞率升至 4%。PPO baseline 成功率从 90% 降至 88%，碰撞率从 10% 升至 12%。前车急刹对所有模型均造成一定影响但幅度不大。PPO aggressive 在此场景下的 mean_lc 达到了 15.88（高于 in_dist 的 14.02），说明模型在急刹场景下增加了变道行为以规避碰撞。

### 2.4 High-Density 场景

高密度场景（50 辆车，初始间距 1 秒）对模型泛化能力提出了最大挑战：
- PPO aggressive 仍保持 98% 成功率和 2% 碰撞率，展现最佳泛化能力。
- PPO baseline 成功率从 90% 降至 86%，碰撞率从 10% 升至 14%，mean_lc 增至 20.76（高于 in_dist 的 14.30），说明高密度场景下需要更多变道操作。
- PPO balanced/comfort 成功率从 80% 降至 78%，碰撞率升至 22%。
- DQN baseline 的 mean_lc 达到 72.80，几乎是 in_dist 的进一步恶化。
- DQN comfort/conservative 和 PPO conservative 成功率进一步下降至 4%。

---

## 三、DQN 与 PPO 对比

### 3.1 整体对比

PPO 在所有 reward 配置和所有场景下均显著优于 DQN。PPO top-3 配置的平均成功率为 88.5%（aggressive），而 DQN top 配置（comfort）的平均成功率仅为 8.5%。

### 3.2 收敛性与稳定性

从训练曲线来看，PPO 在约 20000 步后即达到稳定，而 DQN 在 50000 步内仍呈现缓慢上升或剧烈震荡趋势。Seed 方差箱线图显示 PPO 在不同 seed 间的性能方差远小于 DQN。

### 3.3 DQN Frequent Lane Changes / Reward Hacking

DQN baseline 和 DQN aggressive 出现了明显的频繁变道问题：
- DQN baseline: mean_lc = 68.07 次/episode（PPO aggressive 仅 14.10）
- DQN aggressive: mean_lc = 66.59 次/episode
- 这种频繁变道伴随高碰撞率（94%-98%），说明 DQN 可能在利用 reward 函数中的某些漏洞，而非学习到真正安全的驾驶策略。

DQN balanced 走向另一个极端：mean_lc = 0.00，但碰撞率 = 100%，mean_reward 仅 4.79。这说明 DQN 在 balanced reward 下完全未能学习到有效的变道策略，在高速行驶（mean_speed = 29.54 m/s）时频繁碰撞。

### 3.4 原因分析

DQN 作为 off-policy 算法，在本任务中表现不佳的可能原因：
1. OccupancyGrid 观测状态空间较大，Q 值函数难以准确估计。
2. 经验回放中混合了不同策略的旧数据，在高随机性环境中可能引入偏差。
3. 离散动作空间中的 ε-greedy 探索策略在高速公路场景下效率较低。
4. PPO 的 clipped objective 天然限制了策略更新幅度，在需要稳定控制的自动驾驶任务中具有优势。

---

## 四、五种 Reward 配置对比

### 4.1 Aggressive

- **PPO**: 最佳综合表现，成功率高，碰撞率低。高速行驶中积极主动变道。
- **DQN**: 频繁变道，碰撞率极高。reward 函数设计对 DQN 无效。

### 4.2 Baseline

- **PPO**: 表现良好，成功率 88.5%，碰撞率 11.5%，是较为均衡的选择。
- **DQN**: 频繁变道 + 高碰撞率，策略失控。

### 4.3 Balanced

- **PPO**: 偏保守策略，mean_lc 仅 0.10，成功率 79.5%，碰撞率 20.5%。适合注重乘坐舒适性的场景。
- **DQN**: 完全失败，100% 碰撞率。

### 4.4 Comfort

- **PPO**: 与 balanced 表现几乎相同，mean_lc = 0.10。这说明 comfort 和 balanced 的权重设置在 PPO 下行为趋同。
- **DQN**: 成功率仅 8.5%，碰撞率 91.5%，但 mean_reward 相对较高（40.44），因为不发生碰撞时速度较高（~25 m/s）。

### 4.5 Conservative

- **PPO 和 DQN**: 两者表现均差，成功率仅 8.5%，碰撞率 91.5%。Conservative 的权重设置过于保守，导致模型未学习到有效策略。
- 这是一个典型案例：过于保守的 reward 设计反而导致更差的安全表现。

---

## 五、Success Rate / Collision Rate / Mean Reward / Mean Speed / Mean LC 综合分析

### 5.1 高回报 ≠ 安全策略

本实验最重要的发现之一是：**不能仅凭 mean_reward 评价模型**。

| 模型 | Mean Reward | Success | Collision | 评价 |
|------|-------------|---------|-----------|------|
| PPO aggressive | 163.40 | 0.975 | 0.025 | ★★★★★ 最佳 |
| DQN aggressive | 64.21 | 0.020 | 0.980 | ★☆☆☆☆ 危险 |
| DQN comfort | 40.44 | 0.085 | 0.915 | ★★☆☆☆ 差 |

DQN aggressive 的 mean_reward（64.21）高于 PPO baseline（75.19）？不对，75.19 > 64.21。但 DQN comfort（40.44）的 reward 虽然远低于 PPO aggressive，却高于 PPO conservative（1.53）。关键是：DQN aggressive 通过频繁变道获得了较高速度（24.96 m/s），从而获得了速度奖励，但碰撞率高达 98%。

### 5.2 指标相关性

- **Success Rate 与 Collision Rate**: 几乎完全负相关（碰撞即失败）。
- **Mean Speed 与 Success Rate**: 并非越高越好。DQN balanced speed=29.54 但 success=0.00。
- **Mean LC 与 Collision Rate**: DQN baseline 和 aggressive 的 mean_lc 极高（>60），伴随高碰撞率。PPO aggressive 的 mean_lc=14.10 但碰撞率仅 2.5%。

### 5.3 评价建议

建议采用多指标综合评价体系：
1. 安全性: collision_rate（越低越好）
2. 成功率: success_rate（越高越好）
3. 效率: mean_speed（接近目标速度 25 m/s）
4. 舒适性: mean_lc（适中的变道次数，过多=频繁变道，过少=可能不够灵活）

---

## 六、PPO Aggressive 最优结果分析

PPO aggressive 在四个场景下的平均表现为：
- success_rate = 0.975
- collision_rate = 0.025
- mean_reward = 163.40
- mean_speed = 20.36
- mean_lc = 14.10

Aggressive 配置的特点：碰撞惩罚权重较低、速度权重较高。这使得 PPO 在学习过程中更积极地探索变道行为，同时 PPO 的 clipped objective 机制确保了策略更新不会过度激进，在探索与安全之间取得了平衡。

PPO aggressive 在各个 OOD 场景下表现稳定：
- 高密度场景成功率仍为 98%，碰撞率 2%。
- 急刹场景成功率 96%，碰撞率 4%。
- 展现了良好的泛化能力。

---

## 七、PPO Balanced / Comfort 保守驾驶倾向

PPO balanced 和 PPO comfort 表现出几乎一致的行为：
- mean_lc = 0.10（几乎不变道）
- success_rate = 0.795
- collision_rate = 0.205
- mean_speed = 21.67

这两种配置对变道和急变速施加了更强惩罚，导致模型倾向于保持车道，较少变道。优点是乘坐舒适性高，缺点是：
1. 在需要变道避让时反应不足，碰撞率（20.5%）高于 aggressive（2.5%）。
2. 平均速度略低，通行效率略低于 baseline。

这说明过度惩罚变道行为可能导致模型在真正需要变道时不够灵活。

---

## 八、OOD 泛化能力总结

| 场景 | PPO aggressive | PPO baseline | Best DQN |
|------|---------------|-------------|----------|
| In-Dist | 0.98 | 0.90 | 0.10 (comfort) |
| Lane Closure | 0.98 | 0.90 | 0.10 (comfort) |
| Sudden Brake | 0.96 | 0.88 | 0.10 (comfort) |
| High Density | 0.98 | 0.86 | 0.06 (baseline) |

结论：
1. PPO 在 OOD 场景下整体保持较好的泛化能力。
2. Lane closure 场景对模型影响最小。
3. High density 对 PPO baseline 的影响最大（success 从 0.90 降至 0.86）。
4. DQN 所有配置在所有场景下表现均差，不存在有效泛化。

---

## 九、总体结论

1. PPO 在本实验的高速公路变道任务中显著优于 DQN。
2. PPO aggressive 是综合性能最优的策略（success=0.975, collision=0.025）。
3. 高回报不一定等于安全策略，必须结合 collision_rate、success_rate、mean_lc 综合评价。
4. 过于保守的 reward 设计（conservative）反而导致更差的安全表现。
5. PPO balanced/comfort 适合注重舒适性、允许较低通行效率的场景。
6. DQN 在 OccupancyGrid + MlpPolicy 设定下存在严重的策略不稳定和 reward hacking 问题。
7. 多场景 OOD 评估是验证模型泛化能力的必要手段。

---

*分析报告结束*
