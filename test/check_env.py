from stable_baselines3.common.env_checker import check_env
from hover_drone_gym.envs.hover_drone_env import HoverDroneEnv

env = HoverDroneEnv()
# to check custom environment and output additional warnings if needed
check_env(env)