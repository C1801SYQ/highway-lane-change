# highway-env 高速公路自主变道决策

> DQN vs PPO + 多目标奖励塑形 + OOD 泛化测试

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 验证环境可创建
python -c "import highway_env; highway_env.register_highway_envs(); import gymnasium as g; e=g.make('highway-fast-v0'); print(e.reset())"

# 3. 训练一个模型（~15min CPU）
python train_dqn.py --reward balanced --seed 42 --steps 50000

# 4. 评估模型
python eval.py --algo dqn --reward balanced --seed 42 --scene in_dist --n-episodes 10

# 5. 批量跑（快速模式）
bash run_batch.sh --quick          # Linux/macOS
run_batch.bat --quick              # Windows
```

## 最小验收流程（15分钟）

```bash
pip install -r requirements.txt
python train_dqn.py --reward baseline --seed 42 --steps 10000
python train_ppo.py --reward balanced --seed 42 --steps 10000
python eval.py --algo dqn --reward baseline --seed 42 --scene in_dist --n-episodes 5
python eval.py --algo ppo --reward balanced --seed 42 --scene in_dist --n-episodes 5
python scripts/plot_all.py
python eval.py --algo ppo --reward balanced --seed 42 --scene in_dist --n-episodes 1 --render
python select_best.py --algo ppo --reward balanced
bash run_batch.sh --quick          # 或 run_batch.bat --quick
```

## 目录结构

```
highway-lane-change/
├── README.md
├── config.yaml              # 单一事实源
├── requirements.txt
├── make_env.py              # 环境工厂
├── train_dqn.py             # DQN 训练
├── train_ppo.py             # PPO 训练
├── eval.py                  # 评估 + OOD + 录屏
├── select_best.py           # 自动选最优 seed
├── run_batch.sh             # Linux/macOS 批量
├── run_batch.bat            # Windows 批量
├── scripts/
│   ├── plot_curves.py
│   ├── plot_seeds.py
│   ├── plot_reward.py
│   └── plot_all.py
└── utils/
    ├── __init__.py
    ├── logging.py
    ├── reward.py
    └── ood_scenarios.py
```

## 环境

- Python >= 3.9
- 纯 CPU 运行
- highway-fast-v0 (GrayscaleImage + FrameStack(4))
- 自动 fallback 到 OccupancyGrid（若 GrayscaleImage 不可用）

---

## 期末大作业结题说明

### 项目题目

**《基于 DQN 与 PPO 的高速公路自主变道决策研究》**

### 快速运行命令

```bash
# Linux/macOS 一键运行
bash run_final_quick.sh

# Windows 一键运行
run_final_quick.bat
```

### 期末推荐实验流程

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 训练（各约 10 分钟 CPU）
python train_dqn.py --reward baseline --seed 42 --steps 10000 --eval-episodes 5
python train_ppo.py --reward balanced --seed 42 --steps 10000 --eval-episodes 5

# 3. 评估
python eval.py --algo dqn --reward baseline --seed 42 --scene in_dist --n-episodes 5
python eval.py --algo ppo --reward balanced --seed 42 --scene all --n-episodes 5

# 4. 生成图表
python scripts/plot_all.py

# 5. 选最优模型
python select_best.py --algo dqn --reward baseline
python select_best.py --algo ppo --reward balanced
```

### 结题材料位置

| 材料 | 位置 | 说明 |
|------|------|------|
| 大作业报告模板 | `docs/report_template.md` | 约 2000 字，复制到 Word 排版即可 |
| 2 分钟视频讲稿 | `docs/video_script_2min.md` | 含分段讲稿和录屏步骤 |
| 提交清单 | `docs/submission_checklist.md` | 压缩包结构、应含/不应含文件 |
| 完成计划 | `docs/final_assignment_plan.md` | 评分要求对照、实验计划 |
| 图表输出 | `figures/` | 训练曲线、seed 方差箱线图、reward 分量柱状图 |
| 训练日志 | `logs/` | eval_metrics.csv、eval_reward_components.csv、final_metrics.json |

### 报告关键内容提示

`docs/report_template.md` 已包含完整报告结构：
- 中文摘要 + 英文摘要 + 关键词
- 算法介绍（DQN + PPO 原理与对比）
- 数据集介绍（highway-env 仿真环境、状态/动作空间）
- 程序设计（模块化架构、奖励函数、OOD 测试）
- 实验结果（训练曲线、多配置对比、seed 方差、OOD 泛化）
- 结论
- **工程与社会因素分析**（交通安全、跨文化差异、责任归属、国际视野）

### 评分要求对照

- ✅ 能完成复杂工程问题求解 → 仿真环境 + DQN + PPO + 完整实验流程
- ✅ 能正确分析问题、采用合适算法并优化性能 → 多目标奖励塑形 + 5 种配置对比
- ✅ 能实现多种算法并对比分析优劣 → DQN vs PPO + OOD 泛化 + Seed 方差
- ✅ 工程与社会 → 英文摘要 + 国际视野 + 安全/文化/法律/伦理分析
- ✅ 自编主要算法代码 → 自定义多分量奖励函数、OOD 场景设计、完整评估框架
