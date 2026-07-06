@echo off
REM file: run_batch.bat
REM 批量训练脚本 (Windows)
REM 用法:
REM   run_batch.bat                 完整矩阵 50 次
REM   run_batch.bat --quick         快速模式: 2 algo x 2 reward x 3 seeds = 12次

setlocal enabledelayedexpansion
cd /d "%~dp0"

set QUICK=0
if "%1"=="--quick" set QUICK=1

if %QUICK%==1 (
    echo === QUICK MODE: 2 algo x 2 reward x 3 seeds ===
    set REWARDS=baseline balanced
    set SEEDS=42 123 456
) else (
    echo === FULL MODE: 2 algo x 5 reward x 5 seeds ===
    set REWARDS=baseline comfort aggressive balanced conservative
    set SEEDS=42 123 456 789 1024
)

mkdir logs 2>nul
mkdir models 2>nul
mkdir figures 2>nul

echo algo,reward,seed,best_mean_reward,status > logs\summary.csv

for %%a in (dqn ppo) do (
    for %%r in (%REWARDS%) do (
        for %%s in (%SEEDS%) do (
            echo --- Training: %%a / %%r / seed=%%s ---
            python train_%%a.py --reward %%r --seed %%s
            if exist "logs\%%a\%%r\seed_%%s\final_metrics.json" (
                python -c "import json; d=json.load(open('logs/%%a/%%r/seed_%%s/final_metrics.json')); print(f'  best_mean_reward={d.get(\"best_mean_reward\",\"N/A\")}')"
            )
            echo %%a,%%r,%%s,done >> logs\summary.csv
            echo.
        )
    )
)

echo === BATCH DONE ===
python select_best.py --algo dqn --reward balanced
python select_best.py --algo ppo --reward balanced
endlocal
