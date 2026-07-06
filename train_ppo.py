# file: train_ppo.py
"""PPO 训练入口。用法:
    python train_ppo.py --reward balanced --seed 42
    python train_ppo.py --reward baseline --seed 42 --steps 100000 --resume
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
    return "CnnPolicy" if use_grayscale else "MlpPolicy"


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
    hp = cfg["hyperparams"]["ppo"]
    steps = args.steps or cfg["training"]["total_timesteps"]
    log_dir = cfg["training"]["log_dir"]
    reward_weights = _get_reward_weights(args.reward)

    from utils.logging import make_run_dir, seed_everything, save_config_snapshot
    run_dir = args.save_dir or make_run_dir(log_dir, "ppo", args.reward, args.seed)
    os.makedirs(run_dir, exist_ok=True)

    seed_everything(args.seed)

    # 检测观测方案
    from make_env import make_env, make_vec_env
    _tmp_env, use_gs = make_env(seed=args.seed, reward_weights=None)
    _tmp_env.close()
    policy = _get_policy(use_gs)
    hp_snapshot = dict(hp)
    hp_snapshot["policy"] = policy

    print(f"[PPO] reward={args.reward} seed={args.seed} steps={steps} policy={policy}")
    print(f"[PPO] run_dir={run_dir}")

    train_env = make_vec_env(n_envs=1, seed=args.seed, reward_weights=reward_weights,
                             use_vec_normalize=True)
    eval_env = make_vec_env(n_envs=1, seed=args.seed + 10000, reward_weights=reward_weights,
                            use_vec_normalize=True)

    vn_path = os.path.join(run_dir, "vecnormalize.pkl")
    train_env.save(vn_path)

    from stable_baselines3 import PPO
    model_path = os.path.join(run_dir, "final_model.zip")
    if args.resume and os.path.exists(model_path):
        print(f"[PPO] Resuming from {model_path}")
        model = PPO.load(model_path, env=train_env, seed=args.seed)
    else:
        model = PPO(
            policy=policy,
            env=train_env,
            learning_rate=hp["learning_rate"],
            n_steps=hp["n_steps"],
            batch_size=hp["batch_size"],
            n_epochs=hp["n_epochs"],
            gamma=hp["gamma"],
            gae_lambda=hp["gae_lambda"],
            clip_range=hp["clip_range"],
            ent_coef=hp["ent_coef"],
            vf_coef=hp["vf_coef"],
            seed=args.seed,
            verbose=1,
            tensorboard_log=run_dir,
        )

    from utils.logging import EvalCallback
    eval_cb = EvalCallback(
        eval_env=eval_env, run_dir=run_dir,
        eval_freq=cfg["training"]["eval_freq"],
        n_eval_episodes=args.eval_episodes,
        best_metric="mean_reward",
        verbose=1,
    )

    model.learn(total_timesteps=steps, callback=eval_cb,
                tb_log_name=f"ppo_{args.reward}_seed{args.seed}")

    model.save(model_path)
    train_env.save(vn_path)

    save_config_snapshot(run_dir, {
        "algo": "PPO", "reward_cfg": args.reward, "seed": args.seed,
        "policy": policy, "use_grayscale": use_gs,
        "total_steps": steps, "best_mean_reward": eval_cb.best_value,
        "hyperparams": hp_snapshot,
    })

    from utils.logging import save_final_json
    save_final_json(run_dir, {
        "algo": "PPO", "reward_cfg": args.reward, "seed": args.seed,
        "best_mean_reward": eval_cb.best_value,
        "success_rate": eval_cb.best_sr if hasattr(eval_cb, 'best_sr') else None,
    })

    train_env.close()
    eval_env.close()
    print(f"[PPO] Done. Model: {model_path}")


if __name__ == "__main__":
    main()
