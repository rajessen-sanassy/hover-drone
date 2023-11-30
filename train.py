import os
from hover_drone_gym import HoverDroneEnv
from stable_baselines3 import DQN, PPO
from sb3_contrib import QRDQN
# from sbx import PPO
from stable_baselines3.dqn.policies import MultiInputPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
import wandb
from wandb.integration.sb3 import WandbCallback

def train(env):
    run = wandb.init(
        project="hoverdrone",
        sync_tensorboard=True,
        monitor_gym=True,
    )

    log_dir = "tmp/"
    os.makedirs(log_dir, exist_ok=True)

    env = Monitor(env, log_dir)

    # policy_kwargs = dict(n_quantiles=50, net_arch=[256, 256, 256, 256]) # QRDQN
    policy_kwargs = dict(net_arch=[256, 256, 256, 256])
    model = QRDQN("MultiInputPolicy", env, gamma=0.9975, learning_rate=3e-4, batch_size=64, policy_kwargs=policy_kwargs, verbose=1)
    # model = TQC("MultiInputPolicy", env, top_quantiles_to_drop_per_net=2, verbose=1)
    # model = PPO("MultiInputPolicy", env, verbose=1, gamma=0.9975, ent_coef=0.01, policy_kwargs=policy_kwargs, tensorboard_log=log_dir)
    print(model.policy)
    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=log_dir, name_prefix="PPO_Nov_30_12_43"
    )

    # Train the agent
    model.learn(
        total_timesteps=10000000,
        callback=[
            checkpoint_callback,
            WandbCallback(
                gradient_save_freq=100000,
                model_save_path=f"models/{run.id}",
                model_save_freq=100000,
                verbose=2,
            ),
        ],
    )

def main():
    env = HoverDroneEnv(render=False, continuous=False)

    train(env)

if __name__ == "__main__":
    main()