import os
import time
from hover_drone_gym import HoverDroneEnv
from stable_baselines3 import DQN, PPO, TD3, SAC
from sb3_contrib import QRDQN, TQC
# from sbx import PPO
from stable_baselines3.dqn.policies import MultiInputPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
import wandb
from wandb.integration.sb3 import WandbCallback
from datetime import datetime

def train(env, models, log_dir, load=False):
    model_name = "TQC"

    run = wandb.init(
        project="hoverdrone",
        sync_tensorboard=True,
        monitor_gym=True,
    )
    
    model = models[model_name]

    print(model.policy)
    time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=log_dir, name_prefix=f"{model_name}_{time}"
    )

    # Train the agent
    # if load:
        # model = QRDQN.load("tmp/rl_model_v1_10000000_steps.zip", env, gamma=0.9975, learning_rate=3e-4, batch_size=64, verbose=1)
    model.learn(
        total_timesteps=100000000,
        callback=[
            checkpoint_callback,
            WandbCallback(
                gradient_save_freq=100000,
                model_save_path=f"models/{model_name}_{time}",
                model_save_freq=100000,
                verbose=2,
            ),
        ],
    )

def main():
    log_dir = "tmp/"
    os.makedirs(log_dir, exist_ok=True)

    env = HoverDroneEnv(render=False, visualize=False, continuous=True)
    env = Monitor(env, log_dir)

    policy_kwargs0 = dict(n_quantiles=50, net_arch=[256, 256, 256, 256]) # QRDQN
    policy_kwargs1 = dict(net_arch=[256, 256, 256, 256])

    models = {
        # "PPO": PPO("MultiInputPolicy", env, verbose=1, gamma=0.9975, ent_coef=0.01, policy_kwargs=policy_kwargs1),
        # "QRDQN": QRDQN("MultiInputPolicy", env, gamma=0.9975, learning_rate=3e-4, batch_size=64, policy_kwargs=policy_kwargs0, verbose=1),
        # "DQN": DQN("MultiInputPolicy", env, verbose=1),
        "TQC": TQC("MultiInputPolicy", env, gamma=0.9975, learning_rate=3e-4, policy_kwargs=policy_kwargs1, top_quantiles_to_drop_per_net=2, verbose=1),
    }

    train(env, models, log_dir, load=False)

if __name__ == "__main__":
    main()