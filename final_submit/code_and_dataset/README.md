# 基于 DQN 与 PPO 的高速公路自主变道决策研究 — 程序代码及数据集

## 项目简介

本目录包含《模式识别与机器学习》课程大作业的全部程序代码、配置文件和实验结果数据。

## 环境要求

- Python 3.8+
- 依赖包: 见 requirements.txt

安装依赖：

```bash
pip install -r requirements.txt
```

## 目录结构

```
code_and_dataset/
├── README.md               # 本文件
├── config.yaml             # 全局配置文件
├── requirements.txt        # Python 依赖
├── train_dqn.py            # DQN 训练脚本
├── train_ppo.py            # PPO 训练脚本
├── eval.py                 # 模型评估脚本
├── select_best.py          # 最优模型选择脚本
├── make_env.py             # 环境工厂模块
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── reward.py           # 奖励函数定义
│   ├── logging.py          # 日志与回调
│   └── ood_scenarios.py    # OOD 场景定义
├── scripts/                # 可视化脚本
│   ├── plot_all.py
│   ├── plot_curves.py
│   ├── plot_reward.py
│   └── plot_seeds.py
├── docs/                   # 文档
│   ├── final_report.md     # 最终报告
│   ├── final_result_analysis.md  # 结果分析
│   └── report_template.md  # 报告模板
├── figures/                # 实验结果图表 (12 张 PNG)
├── run_logs/               # 汇总结果 CSV
│   ├── final_result_summary.csv
│   ├── final_average_ranking.csv
│   ├── final_ranking_by_scene.csv
│   └── final_check_report.txt
└── logs/                   # 训练与评估日志 (JSON/CSV)
    ├── dqn/
    │   ├── aggressive/
    │   ├── balanced/
    │   ├── baseline/
    │   ├── comfort/
    │   └── conservative/
    └── ppo/
        ├── aggressive/
        ├── balanced/
        ├── baseline/
        ├── comfort/
        └── conservative/
```

## 实验配置

- 算法: DQN, PPO
- 奖励函数: baseline, comfort, aggressive, balanced, conservative
- 随机种子: 42, 123, 456, 789, 1024
- 训练步数: 50000
- 状态观测: OccupancyGrid
- 策略网络: MlpPolicy

## 结果文件说明

- `final_metrics.json`: 每组训练最终指标（50 个）
- `best_selection.json`: 每组合最优模型选择记录（10 个）
- `eval_all.json`: 最优模型 OOD 评估完整记录（10 个）
- `final_result_summary.csv`: 汇总评估结果（40 行）
- `final_average_ranking.csv`: 平均排名

## 注意

- 本目录不包含训练好的模型权重文件（best_model.zip / final_model.zip）
- 本目录不包含 .git 版本控制文件
- 本目录不包含 TensorBoard 事件文件
- 实验在纯 CPU 环境下运行，使用 OccupancyGrid + MlpPolicy
