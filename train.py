import os
import argparse
from hover_drone_gym import HoverDroneEnv
from stable_baselines3 import DQN, PPO, SAC
from sb3_contrib import QRDQN, TQC
from stable_baselines3.dqn.policies import MultiInputPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from datetime import datetime

def _get_args():
    """ Parses the command line arguments and returns them. """
    parser = argparse.ArgumentParser(description=__doc__)

    # Argument for the mode of execution (human or random):
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="TQC",
        choices=["PPO", "QRDQN", "DQN", "SAC", "TQC"],
        help="The execution mode for the game.",
    )

    return parser.parse_args()

def train(env, model, log_dir, model_name, load=False):

    print(model.policy)
    time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    checkpoint_callback = CheckpointCallback(
        save_freq=10000, save_path=log_dir, name_prefix=f"{model_name}_{time}"
    )

    # load and train the agent
    # if load:
    #     model = TQC.load("tmp/TQC_2023-12-04_22:30:23_900000_steps.zip", env, tau=0.01, ent_coef='auto', gamma=0.99, learning_rate=3e-4, batch_size=256, top_quantiles_to_drop_per_net=3, verbose=1)
    
    model.learn(
        total_timesteps=10000000,
        callback=[
            checkpoint_callback
        ],
    )

def main():
    args = _get_args()
    log_dir = "tmp/"
    os.makedirs(log_dir, exist_ok=True)

    policy_kwargs0 = dict(n_quantiles=50, net_arch=[256, 256, 256, 256]) # QRDQN
    policy_kwargs1 = dict(net_arch=[256, 256, 256, 256])

    if args.mode == "PPO":
        env = HoverDroneEnv(render=False, visualize=False, continuous=False)
        env = Monitor(env, log_dir)
        model = PPO("MultiInputPolicy", env, verbose=1, gamma=0.9975, ent_coef=0.01, policy_kwargs=policy_kwargs1)
        train(env, model, log_dir, "PPO", load=False)
    elif args.mode == "QRDQN":
        env = HoverDroneEnv(render=False, visualize=False, continuous=False)
        env = Monitor(env, log_dir)
        model = QRDQN("MultiInputPolicy", env, gamma=0.9975, learning_rate=3e-4, batch_size=64, policy_kwargs=policy_kwargs0, verbose=1)
        train(env, model, log_dir, "QRDQN", load=False)
    elif args.mode == "DQN":
        env = HoverDroneEnv(render=False, visualize=False, continuous=False)
        env = Monitor(env, log_dir)
        model = DQN("MultiInputPolicy", env, verbose=1)
        train(env, model, log_dir, "DQN", load=False)
    elif args.mode == "SAC":
        env = HoverDroneEnv(render=False, visualize=False, continuous=True)
        env = Monitor(env, log_dir)
        model = SAC("MultiInputPolicy", env, tau=0.01, ent_coef='auto', gamma=0.99, learning_rate=3e-4, batch_size=256, policy_kwargs=policy_kwargs1, verbose=1)
        train(env, model, log_dir, "SAC", load=False)
    elif args.mode == "TQC":
        env = HoverDroneEnv(render=False, visualize=False, continuous=True)
        env = Monitor(env, log_dir)
        model = TQC("MultiInputPolicy", env, tau=0.01, ent_coef='auto', gamma=0.99, learning_rate=3e-4, batch_size=256, policy_kwargs=policy_kwargs1, top_quantiles_to_drop_per_net=3, verbose=1)
        train(env, model, log_dir, "TQC", load=False)
    else:
        print("Invalid mode!")

if __name__ == "__main__":
    main()