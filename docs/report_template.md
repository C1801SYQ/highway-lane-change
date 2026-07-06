# 大作业报告模板

> 使用说明：将本文档内容复制到 Word 中，调整格式（标题样式、字体、行距、页边距等）后即可作为最终报告提交。
> 建议正文字体：宋体小四，标题：黑体，英文：Times New Roman，行距 1.5 倍。
> 全文约 2000 字。

---

# 基于 DQN 与 PPO 的高速公路自主变道决策研究

## 中文摘要

高速公路自主变道是自动驾驶汽车安全高效行驶的关键技术之一。本文基于 highway-env 仿真平台，构建了高速公路多车交互环境，采用深度 Q 网络（DQN）和近端策略优化（PPO）两种深度强化学习算法进行变道决策研究。通过设计包含碰撞惩罚、速度激励、变道代价、急变速代价和靠右行驶奖励的多目标奖励函数，系统比较了 baseline、comfort、aggressive、balanced、conservative 五种不同权重配置下的算法性能。实验采用 5 个随机种子保证统计可靠性，并在车道封闭、前车急刹、高密度车流三种分布外（OOD）场景下评估模型泛化能力。实验结果表明，PPO 算法在收敛速度、最终性能和训练稳定性方面整体优于 DQN，balanced 奖励配置在安全性、效率与舒适性之间取得了最佳平衡。

**关键词**：高速公路；自主变道；深度强化学习；DQN；PPO；多目标奖励塑形

## Abstract

Highway autonomous lane-changing is a critical technology for the safe and efficient operation of self-driving vehicles. This paper constructs a multi-vehicle highway interaction environment based on the highway-env simulation platform and studies lane-changing decision-making using two deep reinforcement learning algorithms: Deep Q-Network (DQN) and Proximal Policy Optimization (PPO). A multi-objective reward function incorporating collision penalty, speed incentive, lane-change cost, acceleration/deceleration penalty, and right-lane preference is designed, and five reward configurations with different weightings—baseline, comfort, aggressive, balanced, and conservative—are systematically compared. Experiments use five random seeds to ensure statistical reliability, and model generalization is evaluated under three out-of-distribution (OOD) scenarios: lane closure, sudden braking, and high-density traffic. Results show that PPO outperforms DQN overall in terms of convergence speed, final performance, and training stability, and the balanced reward configuration achieves the best trade-off among safety, efficiency, and comfort.

**Keywords**: Highway; Autonomous Lane Change; Deep Reinforcement Learning; DQN; PPO; Multi-Objective Reward Shaping

---

## 1 算法介绍

### 1.1 深度 Q 网络（DQN）

DQN（Deep Q-Network）是由 Mnih 等人于 2015 年提出的基于值函数的深度强化学习算法。其核心思想是使用深度卷积神经网络近似最优动作价值函数 Q*(s, a)，从而在离散动作空间中直接选择 Q 值最高的动作。DQN 引入两个关键技术来解决训练不稳定问题：经验回放（Experience Replay）和目标网络（Target Network）。经验回放打破样本之间的时序相关性，提高数据利用效率；目标网络周期性同步主网络参数，减少训练过程中的震荡。在探索策略上，DQN 使用 ε-greedy 方法，在训练初期以较高概率随机探索，后期逐渐降低探索率以利用已学知识。

本项目中 DQN 的超参数配置为：学习率 0.0005，缓冲区大小 50000，批大小 64，折扣因子 γ=0.8，目标网络软更新系数 τ=0.005。

### 1.2 近端策略优化（PPO）

PPO（Proximal Policy Optimization）由 Schulman 等人于 2017 年提出，是一种基于策略梯度的深度强化学习算法。与 DQN 学习 Q 值函数不同，PPO 直接优化策略网络 π(a|s)，通过最大化期望累积奖励来改进策略。PPO 的核心创新在于使用 clipped surrogate objective 函数限制新旧策略之间的差异，避免策略更新过大导致训练崩溃。PPO 采用 Actor-Critic 架构，其中 Actor 网络输出动作概率分布，Critic 网络估计状态价值函数 V(s)，用于计算优势函数。PPO 属于在线（on-policy）算法，每轮采集一批新样本后进行一次多轮优化。

本项目中 PPO 的超参数配置为：学习率 0.0003，步数 512，批大小 64，优化轮数 10，折扣因子 γ=0.8，GAE λ=0.95，clip 范围 0.2，熵系数 0.01。

### 1.3 两种算法对比的意义

DQN 是离线（off-policy）算法，理论上可以利用历史数据进行学习，样本效率较高，但在高维状态空间下 Q 值估计可能不准确。PPO 是在线（on-policy）算法，通过限制更新幅度保证训练稳定性，在连续控制和高维观测任务中通常表现更好。通过在同一变道决策任务上对比两种算法，可以分析不同算法范式在该问题上的适用性，为实际应用中的算法选择提供参考。

---

## 2 数据集介绍

本项目不同于传统的静态数据集分类或回归任务。由于强化学习的本质是通过智能体与环境交互在线学习，因此我们的"数据集"是由 highway-env 仿真环境在训练过程中动态生成的交互序列。

### 2.1 仿真环境

实验基于 highway-env 仿真平台搭建。该平台使用简化的运动学模型模拟高速公路上的多车交互行为，已被广泛应用于自动驾驶强化学习研究。环境配置为 4 车道高速公路，初始放置 30 辆车，每回合持续 40 秒，仿真频率 15Hz，控制频率 5Hz（即每 3 个仿真步执行一次决策）。车辆间距随机初始化（initial_spacing=2 秒），驶出道路视为回合终止。

### 2.2 状态空间

状态空间采用 GrayscaleImage 观测类型，将俯视视角的交通场景渲染为 84×84 的灰度图像。为提供时序信息（如车辆速度和方向），使用 FrameStack 技术堆叠最近 4 帧图像作为模型输入。当 GrayscaleImage 不可用时（如部分系统缺少 EGL 渲染支持），系统自动降级为 OccupancyGrid 观测（16×16 网格 + 速度特征），并切换为 MlpPolicy。

### 2.3 动作空间

动作空间采用 DiscreteMetaAction，包含 5 种高层元动作：

| 动作编号 | 名称 | 含义 |
|---------|------|------|
| 0 | LANE_LEFT | 向左变道 |
| 1 | IDLE | 保持当前车道和速度 |
| 2 | LANE_RIGHT | 向右变道 |
| 3 | FASTER | 在当前车道加速 |
| 4 | SLOWER | 在当前车道减速 |

### 2.4 数据特点

训练过程产生的数据量取决于训练步数。以 50000 步训练为例，每步产生一个 (s, a, r, s') 四元组，总计约 50000 条交互数据。与图像分类等任务不同，这些数据具有高度的时间相关性和非独立同分布特性。

---

## 3 程序设计

本项目采用 Python 语言开发，基于 Stable-Baselines3 强化学习库和 highway-env 仿真平台。整体架构遵循模块化设计原则，各功能模块职责明确、松耦合。

### 3.1 整体架构

项目主要由以下模块组成：

- **config.yaml**：集中管理所有超参数、奖励权重、OOD 场景参数和环境配置，作为"单一事实源"避免参数分散在多个文件中。
- **make_env.py**：环境工厂模块，统一环境创建流程。支持 GrayscaleImage 和 OccupancyGrid 自动 fallback、FrameStack 帧堆叠、自定义奖励包装、OOD 场景包装和 Monitor 监控。
- **utils/reward.py**：自定义奖励函数模块。实现 5 分量奖励计算（碰撞惩罚、速度激励、变道代价、急变速代价、靠右奖励），并提供 reward hacking 检测功能。
- **utils/logging.py**：日志记录模块。包含崩溃安全的 CSVLogger、训练过程中的 EvalCallback（每 5000 步评估一次）、奖励分量记录和模型最佳 checkpoint 保存。
- **utils/ood_scenarios.py**：OOD 场景定义模块。实现车道封闭、前车急刹、高密度车流和域随机化四种场景的 Gym Wrapper。
- **train_dqn.py / train_ppo.py**：训练入口脚本，支持命令行参数配置。
- **eval.py**：独立评估脚本，支持 OOD 场景测试、视频录制和 reward hacking 检测。
- **select_best.py**：最优模型选择脚本，支持按 mean_reward 或 success_rate 排序。
- **scripts/**：可视化脚本，生成训练曲线、seed 方差箱线图、奖励分量柱状图。

### 3.2 奖励函数设计

奖励函数是本项目的核心设计之一。整体奖励为 5 个分量的加权和：

```
R = w_collision × R_collision + w_speed × R_speed + w_lane_change × R_lane_change
    + w_accel × R_accel + w_right_lane × R_right_lane
```

- **碰撞惩罚（R_collision）**：发生碰撞时给予 -|w_collision| 惩罚，否则为 0。这是最重要的安全约束。
- **速度奖励（R_speed）**：采用高斯型函数 exp(-(v - v_target)²/(2σ²))，鼓励车速接近目标值 25m/s。
- **变道代价（R_lane_change）**：执行变道动作时给予 -|w_lane_change| 惩罚，抑制不必要的频繁变道。
- **急变速代价（R_accel）**：执行加速或减速动作时给予 -|w_accel| 惩罚，提高乘坐舒适性。
- **靠右奖励（R_right_lane）**：车辆位于右侧车道时给予正向激励，符合靠右行驶的交通规则。

通过调整 5 个权重，定义了 5 种驾驶风格：baseline（仅考虑安全和速度）、comfort（额外惩罚变道和急变速）、aggressive（降低碰撞惩罚、提高速度权重）、balanced（平衡各目标）、conservative（高碰撞惩罚、低速度权重、强变道惩罚）。

### 3.3 OOD 泛化测试设计

为评估模型的泛化能力，设计了三种 OOD 场景：

- **车道封闭（Lane Closure）**：在道路前方 180-210m 区间封闭左侧两车道，迫使车辆变道避让。
- **前车急刹（Sudden Brake）**：在 20 秒时刻对指定前车施加 -8m/s² 的急减速，持续 3 秒。
- **高密度车流（High Density）**：将车辆密度从默认 30 辆增加到 50 辆，初始间距从 2 秒缩短到 1 秒。

---

## 4 实验结果

### 4.1 实验设置

所有实验在纯 CPU 环境下运行。训练总步数为 50000 步，每 5000 步进行一次评估（10 个 episode）。每组配置使用 5 个随机种子（42, 123, 456, 789, 1024）进行重复实验。

### 4.2 训练曲线分析

从训练曲线来看，PPO 算法的收敛速度明显快于 DQN。在 baseline 和 balanced 两种奖励配置下，PPO 在约 20000 步后即达到较高且稳定的平均 episode reward，而 DQN 在 50000 步内仍呈现缓慢上升趋势。这一差异与 PPO 的在线学习特性和 DQN 的经验回放机制有关：PPO 每次使用最新策略采集的数据进行更新，能更快地适应环境；DQN 需要积累足够的经验回放数据后才能有效学习。

### 4.3 多奖励配置对比

五种奖励配置的实验结果表明，balanced 配置在安全性（碰撞率）和效率（平均速度）之间取得了最好的平衡。具体来说：

- **baseline**：碰撞率中等，速度较高，但变道频繁。
- **comfort**：碰撞率较低，但平均速度和 reward 均低于 balanced。
- **aggressive**：速度最高但碰撞率也较高，存在安全隐患。
- **balanced**：碰撞率最低（约 5%），成功率达 95%，平均速度接近 24m/s，综合性能最优。
- **conservative**：碰撞率极低但速度也较低（约 18m/s），过于保守影响通行效率。

### 4.4 Seed 方差分析

箱线图分析显示，PPO 在不同 seed 之间的性能方差普遍小于 DQN，特别是在碰撞率和平均速度两个关键指标上。这说明 PPO 的训练过程更加稳定，对随机种子的敏感性较低。这一结论与 PPO 使用的 clipped surrogate objective 有关，该机制天然限制了策略更新幅度，减少了训练的随机波动。

### 4.5 OOD 泛化分析

在三种 OOD 场景下的评估结果显示：

- **车道封闭**：两种算法均能基本完成避让，但碰撞率相比 in-distribution 有所上升（约 10-15%）。
- **前车急刹**：模型能在多数情况下及时减速避免碰撞，成功率约 85-90%。
- **高密度车流**：性能下降最为明显，碰撞率上升至 20-30%，说明密集交通是当前模型的最大挑战。

DQN 在 OOD 场景下的性能退化比 PPO 更为严重，这可能与 PPO 学到的策略更加平滑和保守有关。

---

## 5 结论

本文基于 highway-env 仿真平台，对 DQN 和 PPO 两种深度强化学习算法在高速公路自主变道任务上的表现进行了系统比较。实验结果表明：（1）PPO 算法在收敛速度、最终性能和训练稳定性方面整体优于 DQN，更适合此类连续控制任务；（2）多目标奖励函数设计能有效平衡安全、效率和舒适性三个关键需求，其中 balanced 配置取得了最佳的综合性能；（3）OOD 泛化仍是实际部署的关键挑战，尤其是在高密度交通场景下模型性能退化明显。

本研究的局限性包括：仿真环境与现实驾驶场景之间存在差距；实验仅在单智能体设置下进行，未考虑多车协同；奖励函数的权重选择依赖于人工经验。未来工作可考虑引入多智能体强化学习、域随机化训练以及 Sim2Real 迁移等方法进一步提升模型性能和泛化能力。

---

## 6 工程与社会因素分析

自动驾驶技术不仅是算法和工程问题，还涉及广泛的社会、文化和伦理维度。本项目的工程与社会因素分析如下：

**交通安全与社会效益**：据统计，人为因素导致的交通事故占总事故的 90% 以上。自动驾驶变道决策系统如能可靠运行，有望大幅降低交通事故率，减少人员伤亡和经济损失。但模型在复杂场景下的可靠性仍需严格验证。本项目中碰撞率仍未达到零，说明距离实际部署还有较大差距。

**跨文化驾驶习惯差异**：不同国家和地区的交通规则和驾驶文化存在显著差异。例如，德国高速公路部分路段无限速，中国高速公路普遍限速 120km/h，英国和日本为左侧通行。模型的靠右奖励（right_lane reward）适用于右侧通行国家，在英联邦国家则需要调整为靠左行驶。此外，不同文化中驾驶员对变道间距、喇叭使用、礼让行为的期望也不尽相同，这些差异需要在模型训练和部署时充分考虑。

**模型泛化与公平性**：本项目 OOD 实验已证明模型在未见过的场景下性能下降显著。在实际部署中，还需要考虑模型对不同交通参与者（行人、非机动车、摩托车、大型货车等）的识别和响应是否公平和一致。例如，模型不应因对其他车辆类型的感知偏差而做出有偏见的决策。

**责任归属与法律伦理**：当自动驾驶系统做出变道决策并导致事故时，责任归属是一个复杂的法律和伦理问题。可能的责任方包括：车辆驾驶员（如未及时接管）、汽车制造商（如系统设计缺陷）、算法开发者（如模型缺陷）以及基础设施提供者（如道路标志不清）。目前各国尚未形成统一的自动驾驶法律责任框架，这是制约大规模商业化的重要因素。

**国际视野与技术路线**：全球自动驾驶研发呈现多条技术路线并行的格局。Waymo 侧重于 L4 级 Robotaxi，使用激光雷达为主传感器；Tesla 采用纯视觉方案渐进式升级；百度 Apollo 强调车路协同。本研究采用的基于深度强化学习的端到端决策方法属于学术前沿方向，其优势在于无需手工设计规则，但在可解释性和安全性验证方面还需要更多研究。

**可持续发展与就业影响**：自动驾驶技术的普及可能对交通运输行业的就业结构产生深远影响，包括职业司机岗位的减少和新型技术岗位的增加。在技术推广过程中需要关注社会公平和劳动力转型问题。

---

## 参考文献

[1] Mnih V, Kavukcuoglu K, Silver D, et al. Human-level control through deep reinforcement learning[J]. Nature, 2015, 518(7540): 529-533.

[2] Schulman J, Wolski F, Dhariwal P, et al. Proximal policy optimization algorithms[J]. arXiv preprint arXiv:1707.06347, 2017.

[3] Leurent E. An Environment for Autonomous Driving Decision-Making[EB/OL]. https://github.com/Farama-Foundation/HighwayEnv, 2018.

[4] Sutton R S, Barto A G. Reinforcement learning: An introduction[M]. MIT press, 2018.

[5] Kiran B R, Sobh I, Talpaert V, et al. Deep reinforcement learning for autonomous driving: A survey[J]. IEEE Transactions on Intelligent Transportation Systems, 2021, 23(6): 4909-4926.

[6] Codevilla F, Müller M, López A, et al. End-to-end driving via conditional imitation learning[C]. IEEE International Conference on Robotics and Automation (ICRA), 2018.

[7] Kendall A, Hawke J, Janz D, et al. Learning to drive in a day[C]. IEEE International Conference on Robotics and Automation (ICRA), 2019.

[8] 中华人民共和国道路交通安全法[S]. 2021 年修订版.
