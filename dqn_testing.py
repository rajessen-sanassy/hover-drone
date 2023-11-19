import os

from stable_baselines3 import DQN, PPO
from stable_baselines3.dqn.policies import DQNPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback

import gymnasium as gym
import hover_drone_gym
from hover_drone_gym import HoverDroneEnv

# Create log dir
# log_dir = "logs/"
# os.makedirs(log_dir, exist_ok=True)

# Create and wrap the environment
# env = gym.make("hover_drone_gym/HoverDrone-v0")
env = HoverDroneEnv()
# env = Monitor(env, log_dir)
print(env.action_space)

# Create DQN agent
model = DQN("MlpPolicy", env, verbose=1)
# model = DQNPolicy(env.observation_space, env.action_space, 1e-2)

# Create checkpoint callback
# checkpoint_callback = CheckpointCallback(
#     save_freq=100000, save_path=log_dir, name_prefix="rl_model_v0"
# )

# Train the agent
model.learn(
    total_timesteps=10000000,
    # callback=[
    #     checkpoint_callback
    # ],
)