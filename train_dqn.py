# file: train_dqn.py
"""DQN 训练入口。用法:
    python train_dqn.py --reward balanced --seed 42
    python train_dqn.py --reward baseline --seed 42 --steps 100000 --resume
"""
import argparse, yaml, os, sys

def _load_cfg():
    root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _get_reward_weights(reward_name):
    cfg = _load_cfg()
    r = cfg["reward"].get(reward_name, cfg["reward"]["baseline"])
    return {k: v for k, v in r.items() if k.startswith("w_")}

def _get_policy(use_grayscale):
    """根据观测类型返回 policy 字符串。"""
    if use_grayscale:
        return "CnnPolicy"
    else:
        return "MlpPolicy"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reward", type=str, default="baseline",
                        choices=["baseline","comfort","aggressive","balanced","conservative"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--save-dir", type=str, default=None)
    args = parser.parse_args()

    cfg = _load_cfg()
    hp = cfg["hyperparams"]["dqn"]
    steps = args.steps or cfg["training"]["total_timesteps"]
    log_dir = cfg["training"]["log_dir"]
    reward_weights = _get_reward_weights(args.reward)

    # 目录
    from utils.logging import make_run_dir, seed_everything, save_config_snapshot
    run_dir = args.save_dir or make_run_dir(log_dir, "dqn", args.reward, args.seed)
    os.makedirs(run_dir, exist_ok=True)

    # 固定种子
    seed_everything(args.seed)

    # 创建环境（先建一个临时环境检测 GrayscaleImage 可用性）
    from make_env import make_env, make_vec_env
    _tmp_env, use_gs = make_env(seed=args.seed, reward_weights=None)
    _tmp_env.close()
    policy = _get_policy(use_gs)
    # 更新 config 快照中使用的 policy
    hp_snapshot = dict(hp)
    hp_snapshot["policy"] = policy

    print(f"[DQN] reward={args.reward} seed={args.seed} steps={steps} policy={policy}")
    print(f"[DQN] run_dir={run_dir}")

    # Training env
    train_env = make_vec_env(n_envs=1, seed=args.seed, reward_weights=reward_weights,
                             use_vec_normalize=True)
    # Eval env（独立实例）
    eval_env = make_vec_env(n_envs=1, seed=args.seed + 10000, reward_weights=reward_weights,
                            use_vec_normalize=True)

    # 保存 VecNormalize 统计
    vn_path = os.path.join(run_dir, "vecnormalize.pkl")
    train_env.save(vn_path)

    # 模型
    from stable_baselines3 import DQN
    model_path = os.path.join(run_dir, "final_model.zip")
    if args.resume and os.path.exists(model_path):
        print(f"[DQN] Resuming from {model_path}")
        model = DQN.load(model_path, env=train_env, seed=args.seed)
    else:
        model = DQN(
            policy=policy,
            env=train_env,
            learning_rate=hp["learning_rate"],
            buffer_size=hp["buffer_size"],
            learning_starts=hp["learning_starts"],
            batch_size=hp["batch_size"],
            tau=hp["tau"],
            gamma=hp["gamma"],
            train_freq=hp["train_freq"],
            gradient_steps=hp["gradient_steps"],
            target_update_interval=hp["target_update_interval"],
            exploration_fraction=hp["exploration_fraction"],
            exploration_initial_eps=hp["exploration_initial_eps"],
            exploration_final_eps=hp["exploration_final_eps"],
            seed=args.seed,
            verbose=1,
            tensorboard_log=run_dir,
        )

    # 回调
    from utils.logging import EvalCallback
    eval_cb = EvalCallback(
        eval_env=eval_env, run_dir=run_dir,
        eval_freq=cfg["training"]["eval_freq"],
        n_eval_episodes=args.eval_episodes,
        best_metric="mean_reward",
        verbose=1,
    )

    # 训练
    model.learn(total_timesteps=steps, callback=eval_cb,
                tb_log_name=f"dqn_{args.reward}_seed{args.seed}")

    # 保存
    model.save(model_path)
    train_env.save(vn_path)

    # 配置快照
    save_config_snapshot(run_dir, {
        "algo": "DQN", "reward_cfg": args.reward, "seed": args.seed,
        "policy": policy, "use_grayscale": use_gs,
        "total_steps": steps, "best_mean_reward": eval_cb.best_value,
        "hyperparams": hp_snapshot,
    })

    from utils.logging import save_final_json
    save_final_json(run_dir, {
        "algo": "DQN", "reward_cfg": args.reward, "seed": args.seed,
        "best_mean_reward": eval_cb.best_value,
        "success_rate": eval_cb.best_sr if hasattr(eval_cb, 'best_sr') else None,
    })

    train_env.close()
    eval_env.close()
    print(f"[DQN] Done. Model: {model_path}")


if __name__ == "__main__":
    main()
