# Claude Code 最终收尾任务说明

你现在位于 `D:\highway-lane-change` 项目目录下。请基于本项目已有实验结果，完成《模式识别与机器学习》课程复杂工程问题求解类编程大作业的最终报告、视频讲稿和提交材料整理。

---

## 一、课程大作业要求

课程名称：《模式识别与机器学习》

大作业类型：复杂工程问题求解类编程大作业

教学目标：  
本作业考核学生面向复杂工程问题，选择或设计合适的模式识别与机器学习方法，正确处理数据，实现算法，开展验证并得到结果，分析并形成结论的能力；同时考核学生理解社会文化因素对于机器学习应用产生影响的能力，以及基本的跨文化国际交流能力。

作业要求：

1. 撰写大作业报告，1000 字以上，必须包括：
   - 题目
   - 中文摘要
   - 英文摘要
   - 报告正文

   报告正文提纲至少包括：
   1. 算法介绍
   2. 数据集介绍
   3. 程序设计
   4. 实验结果
   5. 结论

2. 录制程序讲解、运行过程及结果展示视频，时长约 2 分钟。

3. 按以下目录整理文件并提交：

```text
编程大作业.rar
├── 大作业题名.word
├── 大作业题名.video
└── 大作业程序代码及数据集.rar
```

评分标准：

- 70~80 分：能够使用 Python / Matlab / 工具箱或自编程序完成复杂工程问题求解，并提交带英文摘要的大作业报告。
- 81~90 分：在上述基础上，能够正确分析问题，选择合适算法，并优化算法性能。
- 91~100 分：在上述基础上，能够自编主要算法代码，或实现多种不同算法，并对比分析算法优劣。

工程与社会部分占 10%。报告中必须专门设置“工程问题复杂性与社会文化因素分析”章节，体现对社会文化因素、标准规范、实际应用约束和跨文化国际交流能力的理解。需要讨论自动驾驶 / 智能交通中的安全、法规、伦理、用户舒适性、不同国家驾驶文化差异、低成本部署、责任归属等问题。

---

## 二、复杂工程问题特征要求

报告中必须体现本项目符合复杂工程问题特征：

1. 该问题不是一眼就能确定解决方法的问题，需要分析目标、约束和评价指标。
2. 涉及多方面技术因素：感知状态、决策控制、奖励函数、算法稳定性、安全性、舒适性和交通效率。
3. 需要建立抽象模型：将高速公路变道决策建模为强化学习序贯决策问题。
4. 不是单一常规方法即可解决，因此本项目比较 DQN 和 PPO 两类算法，并比较多种 reward 配置。
5. 涉及不确定性、动态性和非线性：周围车辆行为、交通密度、车道关闭、突然刹车等场景会影响决策。
6. 涉及多方利益：自动驾驶车辆自身效率、乘客舒适性、道路其他车辆安全、交通整体效率、法规约束。
7. 具有系统性：包含仿真环境构建、奖励函数设计、强化学习训练、模型评估、OOD 泛化测试、结果可视化等多个模块。

---

## 三、项目背景

项目题目：

《基于 DQN 与 PPO 的高速公路自主变道决策研究》

研究对象：  
高速公路自动驾驶场景下的自主变道决策问题。

任务目标：  
基于 highway-env 仿真环境，使用强化学习方法训练智能体，使车辆能够在高速公路场景下进行安全、高效、相对稳定的行驶和变道决策。通过 DQN 与 PPO 两类算法、五种奖励函数配置、多随机种子训练和 OOD 场景评估，对比不同策略在安全性、效率、舒适性和泛化能力方面的差异。

算法：

- DQN
- PPO

奖励函数配置：

- baseline
- comfort
- aggressive
- balanced
- conservative

实验设计：

- 2 个算法 × 5 种 reward × 5 个 seed = 50 组训练
- 每个算法-reward 组合选出 1 个最佳 seed，共 10 个最佳模型
- 每个最佳模型在 4 个场景下进行 OOD 评估：
  1. in_dist：常规分布内场景
  2. lane_closure：车道关闭场景
  3. sudden_brake：前车突然刹车场景
  4. high_density：高密度交通场景
- 每个场景评估 50 个 episode
- 最终结果共 10 × 4 = 40 行评价记录

重要说明：  
本项目实际运行时，因为 highway-env 的 GrayscaleImage 观测兼容问题，程序自动 fallback 到 OccupancyGrid 观测，并使用 MlpPolicy。报告必须如实写成：

> 实验采用 OccupancyGrid 状态观测，并在图像观测不可用时自动回退；实际训练策略网络采用 MlpPolicy。

不要写成“CNN 图像训练”，不要写成“基于卷积神经网络处理图像输入”。

---

## 四、当前已有实验结果

请严格遵守以下限制：

1. 不要重新训练模型。
2. 不要重新运行 OOD 评估。
3. 不要删除 `logs`、`figures`、`run_logs`。
4. 只允许读取已有结果、生成分析文件、生成报告、生成视频稿、整理提交目录。
5. 所有结论必须来自已有实验结果，不要编造数据。

当前结果已经完成：

- `logs` 中 `final_metrics.json` 数量为 50
- `logs` 中 `best_selection.json` 数量为 10
- `logs` 中 `eval_all.json` 数量为 10
- `run_logs/final_result_summary.csv` 已生成，共 40 行
- `figures` 中已有 12 张图：
  - `reward_components_dqn.png`
  - `reward_components_ppo.png`
  - `seed_variance_aggressive.png`
  - `seed_variance_balanced.png`
  - `seed_variance_baseline.png`
  - `seed_variance_comfort.png`
  - `seed_variance_conservative.png`
  - `training_curves_aggressive.png`
  - `training_curves_balanced.png`
  - `training_curves_baseline.png`
  - `training_curves_comfort.png`
  - `training_curves_conservative.png`

---

## 五、必须使用的真实统计结果

### 1. In-distribution 场景

- PPO aggressive：success_rate=0.98，collision_rate=0.02，mean_reward=163.66，mean_speed=20.34，mean_lc=14.02
- PPO baseline：success_rate=0.90，collision_rate=0.10，mean_reward=76.37，mean_speed=20.66，mean_lc=14.30
- PPO comfort：success_rate=0.80，collision_rate=0.20，mean_reward=66.19，mean_speed=21.71，mean_lc=0.00
- PPO balanced：success_rate=0.80，collision_rate=0.20，mean_reward=66.19，mean_speed=21.71，mean_lc=0.00
- DQN baseline：success_rate=0.06，collision_rate=0.94，mean_reward=24.04，mean_speed=25.35，mean_lc=66.50，存在频繁变道问题。
- DQN aggressive：success_rate=0.02，collision_rate=0.98，mean_reward=59.42，mean_speed=24.96，mean_lc=61.78。
- DQN balanced：success_rate=0.00，collision_rate=1.00，mean_reward=4.80，mean_speed=29.52，mean_lc=0.00。

### 2. High-density 场景

- PPO aggressive：success_rate=0.98，collision_rate=0.02，mean_reward=163.68，mean_speed=20.38，mean_lc=12.48
- PPO baseline：success_rate=0.86，collision_rate=0.14，mean_reward=72.48，mean_speed=20.90，mean_lc=20.76
- PPO comfort：success_rate=0.78，collision_rate=0.22，mean_reward=67.73，mean_speed=21.53，mean_lc=0.00
- PPO balanced：success_rate=0.78，collision_rate=0.22，mean_reward=67.73，mean_speed=21.53，mean_lc=0.00
- DQN baseline：success_rate=0.06，collision_rate=0.94，mean_reward=26.74，mean_speed=25.45，mean_lc=72.80
- DQN aggressive：success_rate=0.02，collision_rate=0.98，mean_reward=78.64，mean_speed=24.97，mean_lc=81.10
- DQN balanced：success_rate=0.00，collision_rate=1.00，mean_reward=4.76，mean_speed=29.60，mean_lc=0.00

### 3. 四个场景平均结果

- PPO aggressive：success_rate=0.975，collision_rate=0.025，mean_reward=163.4025，mean_speed=20.3600，mean_lc=14.10
- PPO baseline：success_rate=0.885，collision_rate=0.115，mean_reward=75.1900，mean_speed=20.7275，mean_lc=16.12
- PPO balanced：success_rate=0.795，collision_rate=0.205，mean_reward=66.5500，mean_speed=21.6675，mean_lc=0.10
- PPO comfort：success_rate=0.795，collision_rate=0.205，mean_reward=66.5500，mean_speed=21.6675，mean_lc=0.10
- DQN comfort：success_rate=0.085，collision_rate=0.915，mean_reward=40.4375，mean_speed=24.9775，mean_lc=0.00
- DQN conservative：success_rate=0.085，collision_rate=0.915，mean_reward=1.5325，mean_speed=24.9775，mean_lc=0.00
- PPO conservative：success_rate=0.085，collision_rate=0.915，mean_reward=1.5325，mean_speed=24.9775，mean_lc=0.00
- DQN baseline：success_rate=0.060，collision_rate=0.940，mean_reward=24.7150，mean_speed=25.3750，mean_lc=68.07
- DQN aggressive：success_rate=0.020，collision_rate=0.980，mean_reward=64.2050，mean_speed=24.9625，mean_lc=66.59
- DQN balanced：success_rate=0.000，collision_rate=1.000，mean_reward=4.7900，mean_speed=29.5400，mean_lc=0.00

### 4. 核心结论

1. PPO 整体明显优于 DQN。
2. PPO aggressive 在四个场景下平均成功率最高、碰撞率最低、平均回报最高，是本实验综合性能最好的策略。
3. PPO baseline 次之，成功率较高，但碰撞率高于 PPO aggressive。
4. PPO balanced 与 PPO comfort 的变道次数明显更少，体现出更保守、更舒适的驾驶倾向，但成功率和回报低于 PPO aggressive。
5. DQN baseline 与 DQN aggressive 出现明显频繁变道现象，mean_lc 很高，且碰撞率高，说明 DQN 在本实验设定下策略稳定性和安全性不足，存在一定 reward hacking 或行为失控倾向。
6. 不能只看 mean_reward，需要综合 success_rate、collision_rate、mean_lc 和 mean_speed 等指标进行评价。

---

## 六、具体任务

### 任务 1：结果完整性检查

请检查并生成：

`run_logs/final_check_report.txt`

内容包括：

- `final_metrics.json` 数量
- `best_selection.json` 数量
- `eval_all.json` 数量
- `final_result_summary.csv` 行数
- `figures` 图像数量和文件名
- 是否满足最终报告要求
- 是否还需要重新训练或重新评估

要求结论写明：

> 不需要重新训练，不需要重新评估，当前实验结果已经满足《模式识别与机器学习》课程大作业报告撰写和视频展示要求。

### 任务 2：生成结果分析文件

读取 `run_logs/final_result_summary.csv`，生成：

1. `run_logs/final_ranking_by_scene.csv`
2. `run_logs/final_average_ranking.csv`
3. `docs/final_result_analysis.md`

分析必须包括：

- 四类场景下的模型表现
- DQN 与 PPO 对比
- 五种 reward 配置对比
- `success_rate`、`collision_rate`、`mean_reward`、`mean_speed`、`mean_lc` 的综合分析
- 对 DQN frequent lane changes / reward hacking 的说明
- 对 PPO aggressive 最优结果的说明
- 对 PPO balanced / PPO comfort 保守驾驶倾向的说明
- 对 OOD 泛化能力的说明
- 说明“高回报不一定等于安全策略”，必须结合碰撞率、成功率和变道次数评价。

### 任务 3：生成最终报告 Markdown

基于 `docs/report_template.md`、`run_logs/final_result_summary.csv`、`figures` 和上述真实结果，生成：

`docs/final_report.md`

报告题目：

《基于 DQN 与 PPO 的高速公路自主变道决策研究》

报告结构必须如下：

1. 中文摘要
2. English Abstract
3. 引言
4. 复杂工程问题分析
5. 算法介绍
6. 数据集 / 仿真环境介绍
7. 程序设计
8. 实验结果与分析
9. 工程问题复杂性与社会文化因素分析
10. 结论
11. 参考文献

报告写作要求：

- 正文建议 3000～5000 字，不能低于 1000 字。
- 语言正式，符合本科《模式识别与机器学习》课程大作业风格。
- 不要像 AI 口吻，不要使用过多空泛套话。
- 数据必须真实，不能编造。
- 结论要基于已有统计结果。
- 尽量体现《模式识别与机器学习》课程中对机器学习方法选择、建模、训练、评估和比较分析的要求。
- 同时体现“复杂工程问题求解”，而不仅仅是“跑了一个强化学习实验”。

报告具体内容要求：

#### 中文摘要

- 约 150～250 字
- 包括研究背景、方法、实验设计、主要结果和结论。

#### English Abstract

- 约 150 words
- 用正式英文撰写
- 体现基本跨文化国际交流能力。

#### 引言

- 说明高速公路自主变道是复杂工程问题。
- 说明其涉及安全、效率、舒适性和泛化能力。
- 说明为什么选择强化学习方法。
- 说明本项目属于《模式识别与机器学习》课程中的机器学习方法综合应用。

#### 复杂工程问题分析

- 对照复杂工程问题七个特征展开。
- 至少写出系统性、不确定性、动态性、非线性、多目标冲突、多方利益、抽象建模需求。
- 说明本项目不是简单分类或回归问题，而是序贯决策问题。
- 说明问题相关各方利益包括乘客、道路其他车辆、交通管理者和系统开发者。

#### 算法介绍

- 介绍强化学习基本建模：状态、动作、奖励、策略、回报。
- 介绍 DQN：价值函数、Q-learning、经验回放、目标网络等。
- 介绍 PPO：策略梯度、clip objective、稳定更新等。
- 对比 DQN 与 PPO 在连续决策和策略稳定性上的差异。
- 可以使用简要公式，例如 Q-learning 目标或 PPO 裁剪目标，但不要堆砌太复杂公式。

#### 数据集 / 仿真环境介绍

- 说明本项目不是传统静态数据集，而是基于 highway-env 的交互式仿真数据。
- 说明环境状态来自车辆交互过程。
- 说明使用 OccupancyGrid 观测，MlpPolicy。
- 说明四种 OOD 场景：in_dist、lane_closure、sudden_brake、high_density。
- 说明评价指标：success_rate、collision_rate、mean_reward、mean_speed、mean_lc。

#### 程序设计

- 说明项目模块结构：
  - `train_dqn.py`
  - `train_ppo.py`
  - `eval.py`
  - `select_best.py`
  - `make_env.py`
  - `utils/reward.py`
  - `utils/logging.py`
  - `scripts/plot_*.py`
- 说明训练流程：
  - 50 组训练
  - 10 个 best seed
  - 4 场景 OOD 评估
  - 图表汇总
- 说明奖励函数设计：
  - baseline
  - comfort
  - aggressive
  - balanced
  - conservative
- 说明日志、模型、结果文件保存方式。
- 说明如何通过 `final_metrics.json`、`best_selection.json`、`eval_all.json` 和 `final_result_summary.csv` 完成结果追踪。

#### 实验结果与分析

必须插入或标出插图位置：

- 【插图：figures/training_curves_aggressive.png】
- 【插图：figures/training_curves_baseline.png】
- 【插图：figures/training_curves_balanced.png】
- 【插图：figures/seed_variance_aggressive.png】
- 【插图：figures/reward_components_ppo.png】
- 【插图：figures/reward_components_dqn.png】

必须包含最终平均结果表，至少包括：

- PPO aggressive
- PPO baseline
- PPO balanced
- PPO comfort
- DQN comfort
- DQN baseline
- DQN aggressive
- DQN balanced

重点分析：

- PPO aggressive 平均 success_rate=0.975，collision_rate=0.025，mean_reward=163.4025，是综合最佳。
- PPO balanced / comfort 的 mean_lc=0.10，更保守。
- DQN baseline mean_lc=68.07，collision_rate=0.940。
- DQN aggressive mean_lc=66.59，collision_rate=0.980。
- DQN balanced collision_rate=1.000，表现最差。
- 说明“高回报不一定等于安全策略”，要结合安全性和舒适性指标。
- 说明实验验证了多算法、多奖励函数、多场景评估的必要性。
- 说明 PPO 在本实验中比 DQN 更稳定。

#### 工程问题复杂性与社会文化因素分析

这是老师评分中“工程与社会”部分，占 10%，必须写得充分。

内容必须包括：

- 自动驾驶变道决策中的安全责任问题。
- 不同国家和地区交通法规差异。
- 不同文化背景下对激进驾驶和保守驾驶的接受程度差异。
- 乘客舒适性与交通效率之间的权衡。
- 自动驾驶系统在真实道路部署时需要遵守标准、法规和伦理约束。
- 机器学习模型的可解释性与可信度问题。
- 低成本部署、计算资源、传感器成本、维护成本问题。
- 国际视野：可以提到智能交通、自动驾驶安全评估、国际研究社区对安全性和泛化能力的关注。

注意：如果无法联网，不要编造具体标准编号。可以写“需要参考自动驾驶安全相关国际标准、交通法规和行业规范”，但不要虚构不存在的标准条款。

#### 结论

- 总结项目完成了复杂工程问题建模、算法实现、实验验证和结果分析。
- 总结 PPO aggressive 最优。
- 总结 balanced / comfort 的保守性。
- 总结 DQN 的不足。
- 说明后续可改进方向：
  - 引入更真实交通流；
  - 增加多目标安全约束；
  - 增加可解释性分析；
  - 加入真实车辆数据或更复杂仿真器；
  - 使用多智能体强化学习或安全强化学习。

#### 参考文献

至少包含：

- DQN 经典论文
- PPO 经典论文
- highway-env 或 autonomous driving simulation 相关资料
- reinforcement learning 经典教材

如果无法联网，请使用通用经典参考，不要编造 DOI，不要编造不存在的文献。

### 任务 4：生成 Word 文档

如果当前 Python 环境有 `python-docx`，请把 `docs/final_report.md` 转换为：

`final_submit/基于DQN与PPO的高速公路自主变道决策研究.docx`

Word 格式要求：

- 中文字体：宋体
- 英文字体：Times New Roman
- 正文：小四
- 一级标题：黑体三号加粗
- 二级标题：黑体四号加粗
- 行距：1.5 倍
- 页边距使用常规报告格式
- 图片居中
- 表格居中
- 尽量插入以下图片：
  - `figures/training_curves_aggressive.png`
  - `figures/training_curves_baseline.png`
  - `figures/training_curves_balanced.png`
  - `figures/seed_variance_aggressive.png`
  - `figures/reward_components_ppo.png`
  - `figures/reward_components_dqn.png`

如果 `python-docx` 不可用，请至少生成：

`docs/final_report_for_word.md`

并明确提示我复制到 WPS / Word 中手动排版。

### 任务 5：生成 2 分钟视频讲稿

生成：

`docs/video_script_final_2min.md`

视频讲稿要求：

- 控制在约 2 分钟。
- 语言适合口头汇报。
- 包含：
  1. 开场和题目
  2. 复杂工程问题背景
  3. DQN 与 PPO 方法
  4. 实验设计：50 组训练、10 个最佳模型、4 个 OOD 场景
  5. 核心结果：PPO aggressive 最优
  6. DQN 的频繁变道和高碰撞问题
  7. 工程与社会因素：安全、舒适、法规、驾驶文化差异
  8. 结论
- 同时生成一个视频录制展示顺序：
  1. 先展示项目目录
  2. 再展示代码结构
  3. 再展示 `final_result_summary.csv`
  4. 再展示 `figures` 图表
  5. 最后展示报告结论

### 任务 6：整理最终提交目录

创建 `final_submit` 目录，结构如下：

```text
final_submit/
├── 基于DQN与PPO的高速公路自主变道决策研究.docx
├── video_script_final_2min.md
├── result_summary/
│   ├── final_result_summary.csv
│   ├── final_average_ranking.csv
│   ├── final_ranking_by_scene.csv
│   └── final_check_report.txt
├── figures/
│   └── 复制 figures 中全部 png 图
└── code_and_dataset/
    ├── README.md
    ├── config.yaml
    ├── requirements.txt
    ├── train_dqn.py
    ├── train_ppo.py
    ├── eval.py
    ├── select_best.py
    ├── make_env.py
    ├── utils/
    ├── scripts/
    ├── docs/
    ├── figures/
    ├── run_logs/
    └── logs/ 中的 json/csv 结果
```

注意：

- `code_and_dataset` 中不要包含 `.git`。
- 不要包含 `__pycache__`。
- 不要包含 `events.out.*`。
- 如果 `best_model.zip` 或 `final_model.zip` 很大，可以不放；但必须保留代码、配置、图表、json/csv 结果。
- 如果可行，请把 `code_and_dataset` 压缩为：

`final_submit/大作业程序代码及数据集.zip`

最后提醒我：

- 还需要我自己录制视频 mp4，并命名为：

`基于DQN与PPO的高速公路自主变道决策研究.mp4`

- 最终提交时应整理为：

```text
编程大作业.rar
├── 基于DQN与PPO的高速公路自主变道决策研究.docx
├── 基于DQN与PPO的高速公路自主变道决策研究.mp4
└── 大作业程序代码及数据集.rar
```

### 任务 7：最后输出完成清单

请在终端最后输出：

1. 是否检查到 `final_metrics=50`、`best_selection=10`、`eval_all=10`、`summary=40` 行。
2. 是否生成 `docs/final_report.md`。
3. 是否生成 Word 文档。
4. 是否生成视频讲稿。
5. 是否生成 `final_submit` 目录。
6. 是否生成 `大作业程序代码及数据集.zip`。
7. 哪些文件需要我人工检查。
8. 是否还缺最终录制的 mp4 视频。

---

## 七、再次强调

- 课程名称必须写为《模式识别与机器学习》。
- 不要写成《复杂工程问题求解》课程。
- 但报告内容必须突出复杂工程问题求解能力。
- 不要重新训练。
- 不要重新评估。
- 不要编造实验数据。
- 所有结论必须来自已有 `logs`、`run_logs` 和 `figures`。
