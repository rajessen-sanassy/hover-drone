import argparse
import time
import gym
import hover_drone_base.game as game
import hover_drone_gym

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


def random_agent_env():
    env = gym.make("hover_drone_gym/HoverDrone-v0")
    env.reset()
    while True:
        env.render()

        # getting random action:
        action = env.action_space.sample()

        # processing:
        obs, reward, done, _, info = env.step(action)

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
        game.main()
    elif args.mode == "random":
        random_agent_env()
    else:
        print("Invalid mode!")

if __name__ == "__main__":
    main()
