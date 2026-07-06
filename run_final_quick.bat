@echo off
REM file: run_final_quick.bat
REM 期末大作业快速运行脚本 (Windows)
REM 功能: 训练 DQN baseline + PPO balanced → 评估 → 生成图表
REM 预计耗时: ~20-30 分钟 (纯 CPU)

setlocal
cd /d "%~dp0"

echo ============================================
echo   期末大作业快速实验
echo   基于 DQN 与 PPO 的高速公路自主变道决策研究
echo ============================================
echo.

REM 创建目录
mkdir logs 2>nul
mkdir figures 2>nul
mkdir videos 2>nul

REM 训练 DQN baseline
echo [1/6] 训练 DQN (baseline, seed=42, 10000 steps)...
python train_dqn.py --reward baseline --seed 42 --steps 10000 --eval-episodes 5
echo.

REM 训练 PPO balanced
echo [2/6] 训练 PPO (balanced, seed=42, 10000 steps)...
python train_ppo.py --reward balanced --seed 42 --steps 10000 --eval-episodes 5
echo.

REM 评估 DQN
echo [3/6] 评估 DQN baseline (in_dist)...
python eval.py --algo dqn --reward baseline --seed 42 --scene in_dist --n-episodes 5
echo.

REM 评估 PPO (全部场景)
echo [4/6] 评估 PPO balanced (all scenes)...
python eval.py --algo ppo --reward balanced --seed 42 --scene all --n-episodes 5
echo.

REM 生成图表
echo [5/6] 生成图表...
python scripts/plot_all.py
echo.

REM 选最优模型
echo [6/6] 选择最优模型...
python select_best.py --algo dqn --reward baseline
python select_best.py --algo ppo --reward balanced
echo.

echo ============================================
echo   实验完成！
echo   训练日志: logs/
echo   图表结果: figures/
echo   报告模板: docs/report_template.md
echo   视频讲稿: docs/video_script_2min.md
echo ============================================

endlocal
