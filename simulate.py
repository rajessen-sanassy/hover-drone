import argparse
import time
from hover_drone_gym import HoverDroneEnv
from sb3_contrib import TQC, QRDQN
from stable_baselines3 import DQN, PPO, TD3, SAC

def _get_args():
    """ Parses the command line arguments and returns them. """
    parser = argparse.ArgumentParser(description=__doc__)

    # Argument for the mode of execution (human or random):
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="human",
        choices=["human", "model_QRDQN", "model_PPO", "model_SAC", "model_TQC_1", "model_TQC_2"],
        help="The execution mode for the game.",
    )

    return parser.parse_args()

def run_env(model):    
    vec_env = model.get_env()
    obs = vec_env.reset()
    while True:
        # getting random action:
        action, _ = model.predict(obs, deterministic=True)
        
        # processing:
        obs, reward, done, info = vec_env.step(action)
        vec_env.render()

        print(f"Obs: {obs}\n"
              f"Action: {action}\n"
              f"Reward: {reward}\n"
              f"Done: {done}\n"
              f"Info: {info}\n")

        if done:
            vec_env.reset()

def main():
    args = _get_args()

    if args.mode == "human":
        env = HoverDroneEnv(visualize=False)
        env.run_human()
    elif args.mode == "model_QRDQN":
        model = "performant_models/QRDQN_4000000_steps.zip"
        env = HoverDroneEnv(visualize=True, continuous=False)
        model = QRDQN.load(model, env=env)
        run_env(model)
    elif args.mode == "model_PPO":
        model = "performant_models/PPO_900000_steps.zip"
        env = HoverDroneEnv(visualize=True, continuous=False)
        model = PPO.load(model, env=env)
        run_env(model)
    elif args.mode == "model_SAC":
        model = "tmp/SAC_1300000_steps.zip"
        env = HoverDroneEnv(visualize=True, continuous=True)
        model = SAC.load(model, env=env)
        run_env(model)
    elif args.mode == "model_TQC_1":
        model = "performant_models/TQC_300000_steps.zip"
        env = HoverDroneEnv(visualize=True, continuous=True)
        model = TQC.load(model, env=env)
        run_env(model)
    elif args.mode == "model_TQC_2":
        model = "performant_models/TQC_900000_steps.zip"
        env = HoverDroneEnv(visualize=True, continuous=True)
        model = TQC.load(model, env=env)
        run_env(model)
    else:
        print("Invalid mode!")

if __name__ == "__main__":
    main()
