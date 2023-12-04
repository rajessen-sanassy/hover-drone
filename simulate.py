import argparse
import time
from hover_drone_gym import HoverDroneEnv

def _get_args():
    """ Parses the command line arguments and returns them. """
    parser = argparse.ArgumentParser(description=__doc__)

    # Argument for the mode of execution (human or random):
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="human",
        choices=["human", 'random'],
        help="The execution mode for the game.",
    )

    return parser.parse_args()

def run_env(env):
    env.reset()

    while True:
        # getting random action:
        action = env.action_space.sample()
        
        # processing:
        obs, reward, done, _, info = env.step(action)
        env.render()

        print(f"Obs: {obs}\n"
              f"Action: {action}\n"
              f"Reward: {reward}\n"
              f"Done: {done}\n"
              f"Info: {info}\n")

        time.sleep(1/60)

        if done:
            env.reset()

def main():
    args = _get_args()

    if args.mode == "human":
        env = HoverDroneEnv(visualize=True)
        env.run_human()
    elif args.mode == "random":
        env = HoverDroneEnv(visualize=True)
        run_env(env)
    else:
        print("Invalid mode!")

if __name__ == "__main__":
    main()
