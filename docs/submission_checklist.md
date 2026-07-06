# 期末大作业提交清单

## 提交压缩包结构

```
编程大作业.rar
├── 基于DQN与PPO的高速公路自主变道决策研究.word    ← 大作业报告
├── 基于DQN与PPO的高速公路自主变道决策研究.video   ← 2分钟讲解视频（.mp4）
└── 大作业程序代码及数据集.rar                      ← 代码+数据
```

## 提交文件详情

### 1. 大作业报告（.word）

- **文件名**：`基于DQN与PPO的高速公路自主变道决策研究.docx`
- **来源**：将 `docs/report_template.md` 内容复制到 Word，调整排版
- **要求**：1000 字以上，包含中文摘要、英文摘要、正文（算法介绍、数据集介绍、程序设计、实验结果、结论）、工程与社会因素分析、参考文献
- **参考**：`docs/report_template.md` 已提供完整模板，约 2000 字

### 2. 视频讲解（.video）

- **文件名**：`基于DQN与PPO的高速公路自主变道决策研究.mp4`
- **时长**：约 2 分钟
- **内容**：题目介绍 → 算法说明 → 代码演示 → 结果展示 → 总结
- **参考**：`docs/video_script_2min.md` 提供完整讲稿和录屏步骤
- **格式**：MP4（H.264 编码），建议 1920×1080

### 3. 代码及数据集（.rar）

- **文件名**：`大作业程序代码及数据集.rar`
- **里面包含**：

#### ✅ 应该包含的文件

```
highway-lane-change/
├── README.md                     ← 项目说明
├── config.yaml                   ← 超参数配置（事实源）
├── requirements.txt              ← Python 依赖
├── make_env.py                   ← 环境工厂
├── train_dqn.py                  ← DQN 训练脚本
├── train_ppo.py                  ← PPO 训练脚本
├── eval.py                       ← 评估脚本
├── select_best.py                ← 最优模型选择
├── run_batch.sh                  ← Linux/macOS 批量运行
├── run_batch.bat                 ← Windows 批量运行
├── run_final_quick.sh            ← 期末快速运行（Linux/macOS）
├── run_final_quick.bat           ← 期末快速运行（Windows）
├── scripts/
│   ├── plot_curves.py            ← 训练曲线图
│   ├── plot_seeds.py             ← Seed 方差箱线图
│   ├── plot_reward.py            ← Reward 分量柱状图
│   └── plot_all.py               ← 一键生成全部图表
├── utils/
│   ├── __init__.py
│   ├── logging.py                ← 日志/评估回调
│   ├── reward.py                 ← 自定义奖励函数
│   └── ood_scenarios.py          ← OOD 场景定义
├── docs/
│   ├── final_assignment_plan.md  ← 完成计划
│   ├── report_template.md        ← 报告模板
│   ├── video_script_2min.md      ← 视频讲稿
│   └── submission_checklist.md   ← 提交清单（本文件）
├── models/                       ← 最佳模型文件（可选，见下方说明）
│   └── (best_model.zip 等)
├── figures/                      ← 生成的图表（可选，方便查看）
│   └── (*.png)
└── logs/                         ← 训练日志（可选，建议仅保留少量示例）
    └── (eval_metrics.csv 等)
```

#### ❌ 不应该包含的文件

| 文件/目录 | 原因 |
|-----------|------|
| `__pycache__/` | Python 字节码缓存，自动生成 |
| `*.pyc` | 编译缓存文件 |
| `_midterm_build/` | 期中临时构建文件 |
| `logs/` 中的大量日志文件 | 如果太大（> 100MB），只保留关键 CSV（如 eval_metrics.csv、final_metrics.json） |
| `models/` 中的中间模型 | 只保留 best_model.zip（如果文件不大） |
| `videos/` 中的临时视频 | 录屏过程文件 |
| `.git/` | Git 仓库（如果是从 GitHub clone 的） |
| `.vscode/`, `.idea/` | IDE 配置 |
| `*.tmp`, `*.swp` | 临时文件 |

#### 关于模型文件大小的说明

- 如果 `best_model.zip` 文件大小合理（< 50MB），可以包含在提交中
- 如果模型文件很大（DQN/PPO 的 CNN 模型可能达几十到上百 MB），建议：
  1. 在代码包中不包含模型文件
  2. 在 README 中说明如何重新训练（一行命令即可）
  3. 在报告中附上训练结果截图/表格作为替代
- **"数据集"在强化学习中的特殊性**：本项目的"数据集"本质上是 highway-env 仿真环境生成的交互数据，不需要像传统 ML 项目那样打包 CSV 或图片文件。代码 + 环境配置 = 可复现的完整实验

## 提交前检查清单

- [ ] 报告（Word）已完成并保存
- [ ] 视频（MP4）已录制，时长约 2 分钟
- [ ] 代码已按清单打包，排除 `__pycache__` 和临时文件
- [ ] 代码可在别人电脑上运行（`pip install -r requirements.txt` 后能跑通）
- [ ] `run_final_quick.sh` 或 `run_final_quick.bat` 可一键运行
- [ ] 压缩包完整，解压后文件结构符合要求
- [ ] 压缩包大小合理（建议 < 200MB，如果太大检查是否包含了不必要的模型文件）

## 快速验证命令

提交前在另一台电脑（或新建虚拟环境）上验证：

```bash
# 1. 解压代码包
unzip 大作业程序代码及数据集.rar

# 2. 安装依赖
pip install -r requirements.txt

# 3. 快速运行（约 20 分钟）
bash run_final_quick.sh

# 4. 检查输出
ls logs/ figures/
```

## 常见问题

**Q: 视频文件太大怎么办？**
A: 使用 HandBrake 或 ffmpeg 压缩：
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset fast output.mp4
```

**Q: 模型文件太大怎么办？**
A: 不打包模型，在 README 和报告中说明如何训练。老师更看重代码质量和实验设计，而非预训练模型。

**Q: 报告需要多少字？**
A: 正文（不含摘要和参考文献）至少 1000 字。`docs/report_template.md` 提供约 2000 字的模板。

**Q: 视频需要什么内容？**
A: 题目介绍、算法说明、代码/运行演示、结果展示、总结。必须能听清讲解、看清代码和结果。
