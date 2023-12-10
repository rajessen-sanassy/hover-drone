import gymnasium as gym
from gymnasium import spaces
import numpy as np
from hover_drone_gym.envs.game_logic.game import Game
from hover_drone_gym.envs.game_logic.display import Display

class HoverDroneEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self,
                screen_size=(800, 500),
                _building_gap=120,
                _spawn_distance=400,
                _FPS=60,
                _time_limit=1000,
                render=True,
                continuous=False,
                visualize=True,
                ):
        self._screen_size = screen_size
        self._building_gap = _building_gap
        self._spawn_distance = _spawn_distance
        self._FPS = _FPS
        self._time_limit = _time_limit
        self._time = 0
        self._render_frames = render
        self._last_score = 0
        self._high_score = 0
        self._continuous = continuous
        self._visualize = visualize
        self._game = None
        self._renderer = None

        """
        Initialize the HoverDroneEnv environment.

        Parameters:
            - screen_size: Tuple, size of the screen for rendering (width and height).
            - _building_gap: Int, gap between buildings.
            - _spawn_distance: Int, distance between buildings for spawning.
            - _FPS: Int, frames per second for rendering.
            - _time_limit: Int, time limit for an episode.
            - render: Bool, whether to render frames or not.
            - continuous: Bool, whether to use continuous action space.
            - visualize: Bool, whether to visualize the observation space in environment.

        Sets up the observation and action spaces based on continuous or discrete action.
        """

        if(self._continuous):
            self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        else:
            self.action_space = gym.spaces.Discrete(5)
        
        self.observation_space = spaces.Dict({
            # 'distance_to_target': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            # 'angle_to_target': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            'x_distance_to_target': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            'raycast': spaces.Box(low=-np.inf, high=np.inf, shape=(9,), dtype=np.float32),
            'velocity': spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32),
            'angle': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            'angle_velocity': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            
        })

    def _get_obs(self) -> dict:
        """
        Get the current observation of the environment.

        Returns:
            - Dictionary, current observation.
        """
        return {
            # 'distance_to_target': self._game.get_distance_to_target()/780,
            # 'angle_to_target': self._game.get_angle_to_target(),
            'x_distance_to_target': self._game.get_x_distance()/780,
            'raycast': self._game.get_raycast(),
            'velocity': self._game.get_velocity(),
            'angle': self._game.get_angle(),
            'angle_velocity': self._game.get_angle_velocity(),
        }

    def _get_info(self) -> dict:
        """
        Get additional information about the environment.

        Returns:
            - Dictionary, game score.
        """
        return dict({"score": self._game.score})
    
    def _get_reward(self, dead: bool, case: int) -> float:
        """
        Calculate the reward based on the current state.

        Parameters:
            - dead: Bool, whether the agent is dead.
            - case: Int, reward case identifier.

        Returns:
            - Float, calculated reward.
        """
        reward = 0

        # staying alive 
        # (+1 per 60 frames)
        if(self._game.moving):
            reward += 1/self._FPS

        # Passing obstacle 
        # (+100)
        if(self._game.score > self._last_score):
            self._last_score = self._game.score
            reward += 100    
            if(self._last_score > self._high_score):
                self._high_score = self._last_score
                print(f"New High Score: {self._high_score}")
        
        # Agent dies 
        # (-1000 game is over)
        if dead:
            reward -= 1000

        # CASE 2 REWARD STRUCTURE
        if (case == 2):
            reward -= self._game.get_x_distance() / (500 * self._FPS)
        
        return reward
    
    def step(self, action: int or np.array) -> tuple:
        """
        Execute one step in the environment.

        Parameters:
            - action: Action taken by the agent.

        Returns:
            - Tuple: (observation, reward, terminated, truncated, info)
        """
        reward = 0
        self._time += 1 / self._FPS
        dead = self._game.action(action)
        obs = self._get_obs()
        reward = self._get_reward(dead, case=2)
        
        if self._render_frames:
            self.render(reward)

        terminated = dead
        truncated = False
        info = {"score": self._game.score}
        
        # time exit case
        if self._time > self._time_limit:
            terminated = True
        
        return obs, reward, terminated, truncated, info
    
    def reset(self, seed=None) -> tuple:
        """
        Reset the environment to the initial state.

        Parameters:
            - seed: Seed for randomization.

        Returns:
            - Tuple: (observation, info)
        """
        super().reset(seed=seed)
        self._game = Game(screen_size=self._screen_size, 
                          building_gap=self._building_gap, 
                          spawn_rate=self._spawn_distance, 
                          continuous=self._continuous)
        self._game.reset()
        self._last_score = 0
        self._time = 0

        if self._renderer is not None:
            self._renderer.game = self._game

        return self._get_obs(), self._get_info()

    def render(self, reward=None) -> None:
        """
        Render the current state of the environment.

        Parameters:
            - reward: Optional, reward value to display in rendering.

        Renders the environment state using the designated renderer.
        """
        if self._renderer is None:
            self._renderer = Display(screen_size=self._screen_size,
                                     FPS=self._FPS,
                                     visualize=self._visualize)
            self._renderer.game = self._game
            self._renderer.make_display()

        self._renderer.draw_surface(reward)
        self._renderer.update_display()
    
    def run_human(self) -> None:
        """
        Run the environment in human mode for manual interaction.

        Raises:
            - RuntimeError if attempting to run with continuous action space.

        Resets the environment and allows manual control, updating the rendering accordingly.
        """
        if self._continuous:
            raise RuntimeError(
                "Cannot run continuous action space in human mode."
            )
        self.reset()
        reward = 0
        while True:
            dead = self._game.action()
            reward += self._get_reward(dead, case=2)
            self.render(reward)

            if dead:
                reward = 0
                self.reset()

    def close(self) -> None:
        """
        Close the environment.

        Closes the renderer and performs necessary cleanup.
        """
        if self._renderer is not None:
            self._renderer = None
            import pygame
            pygame.display.quit()
            pygame.quit()
        super().close()