import os
from hover_drone_gym import HoverDroneEnv
from stable_baselines3 import DQN, PPO
from stable_baselines3.dqn.policies import MultiInputPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
# from stable_baselines3.common.vec_env import SubprocVecEnv


def test(model):
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

def main():
    env = HoverDroneEnv()

   # Define the policy with MultiInputPolicy
    policy = MultiInputPolicy

    # Create the PPO model
    model = PPO("MultiInputPolicy", env, verbose=1)

    test(model)

if __name__ == "__main__":
    main()
