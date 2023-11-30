import pygame
from pygame.locals import *
from pygame.sprite import *

BUILDING_WIDTH = 80
BUILDING_HEIGHT = 560

class Building():
    def __init__(self, x, y, position, building_gap):
        self._rect = pygame.Rect(x, y, BUILDING_WIDTH, BUILDING_HEIGHT)
        self._passed = False
        self._position = position
        self._building_gap = building_gap

        if position == 1: 
            self._rect.bottomleft = [x, y - self._building_gap]
        elif position == -1:
            self._rect.topleft = [x, y + self._building_gap]
    
    def get_rect_lines(self):
        x, y = self._rect.x, self._rect.y
        w, h = self._rect.width, self._rect.height

        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)
        return [(bottom_left, top_left), (bottom_right, bottom_left),
                (top_left, top_right), (top_right, bottom_right)]
    
    def evaluate(self, x):
        if(x > self._rect.right and not self._passed):
            self._passed = True
            return True
        return False
    
    def update(self, velocity_x):
        building_speed = max(velocity_x, 0)
        self._rect.x -= building_speed
        
        if self._rect.right < 0:
            return True
        return False

    @property
    def position(self): 
        return self._position
    
    @property
    def position_x(self): 
        return self._rect.x
    
    @property
    def position_y(self): 
        return self._rect.y
    
    @property
    def passed(self): 
        return self._passed