import argparse
import time
import gym
import hover_drone_base.hover_drone as hover_drone
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
    score = 0
    while True:
        env.render()

        # getting random action:
        action = env.action_space.sample()

        # processing:
        obs, reward, done, _, info = env.step(action)

        score += reward
        print(f"Obs: {obs}\n"
              f"Action: {action}\n"
              f"Score: {score}\n"
              f"Done: {done}\n"
              f"Info: {info}\n")

        time.sleep(1 / 30)

        if done:
            time.sleep(1)
            score = 0
            env.reset()

def main():
    args = _get_args()

    if args.mode == "human":
        hover_drone.main()
    elif args.mode == "random":
        random_agent_env()
    else:
        print("Invalid mode!")

if __name__ == "__main__":
    main()
