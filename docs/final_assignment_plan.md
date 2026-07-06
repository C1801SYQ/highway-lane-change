# 期末大作业完成计划

## 项目题目

**《基于 DQN 与 PPO 的高速公路自主变道决策研究》**

## 本项目为什么属于"复杂工程问题"

根据《复杂工程问题求解》课程要求，本项目满足以下复杂工程问题特征：

1. **需要建立数学模型和仿真环境** — 高速公路自主变道决策涉及多车交互、连续状态空间和离散动作空间，需要使用 highway-env 仿真平台建立精确的环境模型，包括状态空间（GrayscaleImage 观测）、动作空间（DiscreteMetaAction，5 种元动作）、奖励函数设计（安全、效率、舒适多目标）。

2. **需要比较多种算法** — 项目实现了 DQN（基于值函数）和 PPO（基于策略梯度）两种主流深度强化学习算法，并对它们在相同任务上的性能进行系统对比。

3. **涉及多目标冲突与权衡** — 自动驾驶变道决策需要同时优化安全性（碰撞避免）、效率（高速行驶）、舒适性（减少急加速/急减速/频繁变道）等多个相互冲突的目标。项目通过多目标奖励塑形设计了 5 种不同偏好的奖励配置（baseline、comfort、aggressive、balanced、conservative）。

4. **需要多随机种子实验** — 强化学习训练具有随机性，单一 seed 的结果不可靠。本项目对每个配置使用 5 个随机种子（42, 123, 456, 789, 1024）进行重复实验，通过统计方法（均值±标准差、箱线图）保证结论的可信度。

5. **需要 OOD 分布外泛化测试** — 实际部署中环境必然与训练分布不同。项目设计了车道封闭（Lane Closure）、前车急刹（Sudden Brake）、高密度车流（High Density）三种 OOD 场景，评估模型在未见过的环境中的泛化能力。

6. **涉及工程与社会因素** — 自动驾驶决策系统直接影响交通安全、交通效率和公众接受度。项目分析了跨文化驾驶习惯差异、安全责任归属、模型公平性等工程与社会维度。

## 对照评分要求

### 能完成复杂工程问题求解（70~80 分基础）

- [x] highway-env 仿真环境搭建
- [x] DQN 和 PPO 两种算法实现
- [x] 训练、评估、可视化完整流程
- [x] 多随机种子实验

### 能正确分析问题、采用合适算法并优化性能（81~90 分）

- [x] 多目标奖励塑形（5 种配置）
- [x] 训练曲线对比
- [x] Seed 方差分析
- [x] 碰撞率、成功率、平均速度等指标评估

### 能实现多种算法并对比分析优劣（91~100 分）

- [x] DQN vs PPO 系统对比
- [x] OOD 泛化测试（3 种场景）
- [x] Reward Hacking 检测
- [x] 自定义 reward 组件分析
- [x] 工程与社会因素分析

## 大作业报告结构建议

报告应写在 Word 中，结构如下：

### 题目
基于 DQN 与 PPO 的高速公路自主变道决策研究

### 中文摘要（约 150 字）
概述：高速公路自主变道是自动驾驶的关键技术。本文基于 highway-env 仿真平台，采用 DQN 和 PPO 两种深度强化学习算法进行变道决策研究。通过设计包含安全性、效率、舒适性的多目标奖励函数，比较了 5 种不同权重配置下的算法性能。实验使用 5 个随机种子保证统计可靠性，并在车道封闭、前车急刹、高密度车流三种 OOD 场景下评估模型泛化能力。结果表明，PPO 整体优于 DQN，balanced 奖励配置在安全与效率之间取得了最佳平衡。

### 英文摘要（约 150 words）
概述：Highway autonomous lane-changing is a critical technology for self-driving vehicles. This paper studies lane-changing decision-making using DQN and PPO deep reinforcement learning algorithms based on the highway-env simulation platform. A multi-objective reward function incorporating safety, efficiency, and comfort is designed, and five reward configurations with different weightings are compared. Experiments use five random seeds to ensure statistical reliability, and model generalization is evaluated under three OOD scenarios: lane closure, sudden braking, and high-density traffic. Results show that PPO outperforms DQN overall, and the balanced reward configuration achieves the best trade-off between safety and efficiency.

### 关键词
高速公路；自主变道；深度强化学习；DQN；PPO；多目标奖励塑形

### 正文

#### 1. 算法介绍
- **DQN（Deep Q-Network）**：基于值函数的强化学习算法，使用 CNN 处理图像观测，经验回放和目标网络稳定训练。离散动作空间下通过 ε-greedy 策略平衡探索与利用。
- **PPO（Proximal Policy Optimization）**：基于策略梯度的算法，通过 clipped surrogate objective 限制策略更新幅度，训练更稳定。使用 Actor-Critic 架构，适合连续控制和高维观测。
- **对比意义**：DQN 是离线（off-policy）算法，样本效率较低但实现简单；PPO 是在线（on-policy）算法，通常收敛更快、最终性能更好。

#### 2. 数据集介绍
- 本项目不是传统静态数据集分类任务，而是基于 **highway-env 仿真环境**生成交互式数据。
- 状态空间：GrayscaleImage（84×84×4 帧堆叠），自动 fallback 到 OccupancyGrid
- 动作空间：DiscreteMetaAction，5 种元动作（LANE_LEFT, IDLE, LANE_RIGHT, FASTER, SLOWER）
- 环境参数：4 车道、30 辆车、持续 40 秒、仿真频率 15Hz、策略频率 5Hz
- 训练数据通过 agent 与环境交互在线生成，每个 step 产生 (s, a, r, s') 四元组

#### 3. 程序设计
- **环境工厂**（make_env.py）：统一环境创建，支持 GrayscaleImage/OccupancyGrid 自动 fallback、FrameStack、自定义 reward、OOD wrapper、Monitor
- **奖励函数**（utils/reward.py）：5 个分量（collision, speed, lane_change, accel, right_lane），高斯型速度奖励
- **训练脚本**（train_dqn.py, train_ppo.py）：基于 Stable-Baselines3，支持 resume、config 快照、VecNormalize
- **评估脚本**（eval.py）：独立评估，支持 OOD 场景、reward hacking 检测、视频录制
- **批量运行**（run_batch.sh/bat）：支持 quick/full 模式，自动汇总结果
- **可视化**（scripts/plot_*.py）：训练曲线、seed 方差箱线图、reward 分量柱状图
- **配置管理**（config.yaml）：单一事实源，所有超参数集中管理

#### 4. 实验结果
- 训练曲线：PPO 收敛速度通常快于 DQN，最终 reward 也更高
- 碰撞率与成功率：balanced 配置在低碰撞率和高成功率之间取得最佳平衡
- Seed 方差：PPO 的 seed 间方差通常小于 DQN，训练更稳定
- Reward 分量：不同配置下 5 个分量的贡献差异明显，验证了多目标设计的有效性
- OOD 泛化：在车道封闭和高密度场景下，模型性能有所下降，说明泛化仍是一个挑战

#### 5. 结论
- PPO 在高速公路变道任务上整体优于 DQN
- 多目标奖励设计能有效平衡安全、效率、舒适性
- balanced 配置是推荐的默认选择
- OOD 泛化仍是实际部署的关键瓶颈，需要进一步研究
- 未来方向：引入多智能体交互、更复杂的感知输入、Sim2Real 迁移

#### 6. 工程与社会因素分析
- **交通安全**：自动驾驶变道决策直接影响道路交通安全，模型的可靠性至关重要。碰撞率应趋近于零才能满足实际部署需求。
- **交通规则与文化差异**：不同国家和地区的驾驶习惯和交通规则存在显著差异（如右侧通行 vs 左侧通行、变道礼让文化等），模型需要在多样化场景中训练和验证。
- **模型泛化与公平性**：模型在训练分布内表现良好，但在 OOD 场景下性能下降，说明需要更强的泛化能力。同时需考虑模型在不同交通参与者（行人、自行车、摩托车）面前的表现是否公平。
- **责任归属**：自动驾驶系统做出变道决策导致事故时，责任归属（驾驶员、制造商、算法开发者）是重要的法律和伦理问题。
- **国际视野**：自动驾驶是全球性技术挑战，Waymo、Tesla、百度 Apollo 等不同技术路线各有特点，需要在国际比较中定位本研究的贡献和局限。

### 参考文献
（建议至少引用 5-8 篇，包括 highway-env 论文、DQN 论文、PPO 论文、自动驾驶综述等）

## 推荐实验命令

### 最简验收流程（约 15-30 分钟）

```bash
# 安装依赖
pip install -r requirements.txt

# 训练 DQN baseline（~10min CPU）
python train_dqn.py --reward baseline --seed 42 --steps 10000 --eval-episodes 5

# 训练 PPO balanced（~10min CPU）
python train_ppo.py --reward balanced --seed 42 --steps 10000 --eval-episodes 5

# 评估
python eval.py --algo dqn --reward baseline --seed 42 --scene in_dist --n-episodes 5
python eval.py --algo ppo --reward balanced --seed 42 --scene all --n-episodes 5

# 生成图表
python scripts/plot_all.py

# 选最优模型
python select_best.py --algo dqn --reward baseline
python select_best.py --algo ppo --reward balanced
```

### 期末快速运行（一键）

```bash
# Linux/macOS
bash run_final_quick.sh

# Windows
run_final_quick.bat
```

### 如果时间充足（完整实验）

```bash
# 快速模式（12 次训练）
bash run_batch.sh --quick

# 完整模式（50 次训练，需要数小时）
bash run_batch.sh
```

## 提交材料清单

| 材料 | 对应文件 |
|------|----------|
| 大作业报告（Word） | 参考 `docs/report_template.md` 转写 |
| 视频讲解（2 分钟） | 参考 `docs/video_script_2min.md` 录制 |
| 程序代码及数据集 | 整个项目目录打包（排除 `__pycache__`、大模型文件等） |

详细清单见 `docs/submission_checklist.md`。
