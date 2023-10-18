import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from hover_drone_gym.envs.hover_drone_env import HoverDroneEnv
from gym.envs.registration import register

register(
    id='hover_drone_gym/HoverDrone-v0',
    entry_point='hover_drone_gym.envs:HoverDroneEnv',
    max_episode_steps=300,
)