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
                _spawn_rate=4,
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
        return [
            self._game.get_velocity_vector(),
            self._game.y_distance_from_safe_zone(),
            self._game.get_angle_to_target(),
            self._game.get_angle(),
            self._game.get_angle_velocity(),
            self._game.get_velocity_angle_to_target()
        ]

    def _get_info(self):
        return dict({"score": self._game.score})
    
    def step(self, action):
        reward = 0
        dead = self._game.update_state(int(action))
        obs = self._get_obs()

        # reward structure
        # staying alive (+1 per 60 frames)
        reward += 1/self.FPS

        # passing obstacle (+10)
        score = self._game.evaluate()
        self._game.score += score
        if(score):
            reward += 10

        #not within safe zone (-distance from the safe zone)
        reward -= abs(self._game.y_distance_from_safe_zone())       

        #agent dies (-1000 game is over)
        if dead:
            reward -= 1000

        terminated = dead
        truncated = False
        info = {"score": self._game.score}
        self.render()
        return obs, reward, terminated, truncated, info
    
    def reset(self):
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
