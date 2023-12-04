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
        self._continuous = continuous
        self._visualize = visualize
        self._game = None
        self._renderer = None

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

    def _get_obs(self):
        return {
            # 'distance_to_target': self._game.get_distance_to_target()/780,
            # 'angle_to_target': self._game.get_angle_to_target(),
            'x_distance_to_target': self._game.get_x_distance()/780,
            'raycast': self._game.get_raycast(),
            'velocity': self._game.get_velocity(),
            'angle': self._game.get_angle(),
            'angle_velocity': self._game.get_angle_velocity(),
        }

    def _get_info(self):
        return dict({"score": self._game.score})
    
    def _get_reward(self, dead, case):
        reward = 0

        # staying alive 
        # (+1 per 60 frames)
        if(self._game.moving):
            reward += 1/self._FPS

        # Passing obstacle 
        # (+100)
        if(self._game.score > self._last_score):
            print("PASS")
            self._last_score = self._game.score
            reward += 100    
        
        # Agent dies 
        # (-1000 game is over)
        if dead:
            reward -= 1000

        # CASE 2 REWARD STRUCTURE
        if (case == 2):
            reward -= self._game.get_x_distance() / (500 * self._FPS)
        
        return reward
    
    def step(self, action):
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
    
    def reset(self, seed=None):
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

    def render(self, reward=None):
        if self._renderer is None:
            self._renderer = Display(screen_size=self._screen_size,
                                     FPS=self._FPS,
                                     visualize=self._visualize)
            self._renderer.game = self._game
            self._renderer.make_display()

        self._renderer.draw_surface(reward)
        self._renderer.update_display()
    
    def run_human(self):
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

    def close(self):
        if self._renderer is not None:
            self._renderer = None
            import pygame
            pygame.display.quit()
            pygame.quit()
        super().close()