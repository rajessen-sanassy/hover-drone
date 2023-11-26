import gymnasium as gym
from gymnasium import spaces
import numpy as np
from hover_drone_gym.envs.game_logic.game import Game

class HoverDroneEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self,
                screen_size=(800, 500),
                _building_gap=120,
                _spawn_distance=400,
                _FPS=60,
                _time_limit=1000
                ):
        
        self.action_space = gym.spaces.Discrete(4)
        
        self.observation_space = spaces.Dict({
            'raycast': spaces.Box(low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32),
            'velocity': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            'angle': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            'angle_velocity': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
        })

        self._screen_size = screen_size
        self._building_gap = _building_gap
        self._spawn_distance = _spawn_distance
        self._FPS = _FPS
        self._time_limit = _time_limit
        self._time = 0
        self._game = None

    def _get_obs(self):
        return {
            'raycast': self._game.get_raycast(),
            'velocity': [self._game.get_velocity()],
            'angle': [self._game.get_angle()],
            'angle_velocity': [self._game.get_angle_velocity()],
        }

    def _get_info(self):
        return dict({"score": self._game.score})
    
    def _get_reward(self, dead, case):
        reward = 0

        # staying alive 
        # (+1 per 60 frames)
        reward += 1/self._FPS

        # Passing obstacle 
        # (+10)
        score = self._game.evaluate()
        self._game.score += score
        if(score):
            reward += 10    
        
        # Agent dies 
        # (-1000 game is over)
        if dead:
            reward -= 1000

        # CASE 2 REWARD STRUCTURE
        if (case == 2):
            #not within safe zone (-distance from the safe zone)
            reward -= abs(self._game.y_distance_from_safe_zone()) 
            reward -= abs(self._game.x_distance_from_building()) // 2  
        
        return reward
    
    def step(self, action):
        reward = 0
        self._time += 1 / self._FPS
        dead = self._game.update_state(int(action))
        obs = self._get_obs()
        reward = self._get_reward(dead, case=1)

        self.render()

        # time exit case
        if self._time > self._time_limit:
            terminated = True

        terminated = dead
        truncated = False
        info = {"score": self._game.score}
        
        return obs, reward, terminated, truncated, info
    
    def reset(self, seed=None):
        super().reset(seed=seed)
        self._game = Game(self._screen_size, self._building_gap, self._spawn_distance, self._FPS)
        self._game.reset()

        return self._get_obs(), self._get_info()

    def render(self):
        self._game.view()
    
    def run_human(self):
        self._game = Game(self._screen_size, self._building_gap, self._spawn_distance, self._FPS)
        self._game.reset()
        self._game.start()

    def close(self):
        if self._game.window is not None:
            import pygame
            pygame.display.quit()
            pygame.quit()