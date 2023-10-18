import gym
from gym import spaces
import numpy as np
import pygame
from hover_drone_gym.envs.game_logic.hover_drone import HoverDrone

class HoverDroneEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self,
                screen_size=(800, 500),
                _building_gap=120,
                _spawn_rate=6,
                _FPS=60,
                ):
        
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(-np.inf, np.inf,
                                                shape=(2,),
                                                dtype=np.float64)
        self._screen_size = screen_size
        self._building_gap = _building_gap
        self._spawn_rate = _spawn_rate
        self.FPS = _FPS

        self._renderer = None
        self._game = None

    def _get_obs(self):
        return np.array([
            self._game.nearest_building()[0],
            self._game.nearest_building()[1],
        ])

    def _get_info(self):
        return dict({"score": self._game.score})
    
    def step(self, action):
        alive = not self._game.update_state(int(action))
        obs = self._get_obs()
        reward = self._game.score + 0.000001

        terminated = not alive
        truncated = False
        info = {"score": self._game.score}

        return obs, reward, terminated, truncated, info
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._game = HoverDrone(self._screen_size, self._building_gap, self._spawn_rate, self.FPS)
        self._game.reset()

        return self._get_obs(), self._get_info()

    def render(self):
        self._game.view()
    
    def close(self):
        if self._renderer is not None:
            pygame.display.quit()
            self._renderer = None
        super().close()
