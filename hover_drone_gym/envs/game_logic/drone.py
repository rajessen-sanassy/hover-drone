import pygame
from math import sin, cos, pi
from hover_drone_gym.envs.game_logic.physics import Physics

DRONE_WIDTH = 50
DRONE_HEIGHT = 50

class Drone():
    def __init__(self, x, y, continuous):
        self._rect = pygame.Rect(x, y, DRONE_WIDTH, DRONE_HEIGHT)
        self._rect.center = [x,y]
        if continuous:
            self._physics = Physics("continuous")
        else:
            self._physics = Physics("discrete")

        self._velocity_x = 0
        self._velocity_y = 0
        self._is_alive = True

    def action(self, action):
        self._velocity_x, self._velocity_y = self._physics.move(action)

    def update(self):
        if(not self._is_alive):
            return

        #updating the positions 
        self._rect.y += self._velocity_y
        
        return self._velocity_x
    
    def kia(self):
        self._is_alive = False

    def get_rect_lines(self):
        x, y = self._rect.x, self._rect.y
        w, h = self._rect.width, self._rect.height - 35
        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)

        top_left = self._rotate_point(top_left)
        top_right = self._rotate_point(top_right)
        bottom_left = self._rotate_point(bottom_left)
        bottom_right = self._rotate_point(bottom_right)

        # Return the four lines as tuples (start, end)
        return [(top_left, top_right), (top_right, bottom_right),
                (bottom_right, bottom_left), (bottom_left, top_left)]
    
    def _rotate_point(self, point):
        cx, cy = self._rect.center
        px, py = point

        angle_radian = self.angle * pi / 180
        # Calculate the rotated coordinates
        rotated_x = cx + cos(-angle_radian) * (px - cx) - sin(-angle_radian) * (py - cy)
        rotated_y = cy + sin(-angle_radian) * (px - cx) + cos(-angle_radian) * (py - cy)

        return int(rotated_x), int(rotated_y)

    @property
    def position(self): 
        return (self.position_x, self.position_y)
    
    @property
    def position_x(self): 
        return self._rect.center[0]
    
    @property
    def position_y(self): 
        return self._rect.center[1]-18
    
    @property
    def velocity_x(self): 
        return self._velocity_x
    
    @property
    def velocity_y(self): 
        return self._velocity_y
    
    @property
    def angle(self): 
        return self._physics.angle
    
    @property
    def angular_speed(self): 
        return self._physics.angular_speed