import pygame
from pygame.locals import *
from pygame.sprite import *

#creating buildings 
class Building(pygame.sprite.Sprite):
    def __init__(self,x,y,position, building_gap, building_image):
        pygame.sprite.Sprite.__init__(self)
        self.image = building_image
        self.rect = self.image.get_rect()
        self.passed = False
        self.pos = position
        self.building_gap = building_gap

        if position == 1:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x,y - self.building_gap]
        if position == -1:
            self.rect.topleft = [x,y + self.building_gap]
    
    def get_rect_lines(self):
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height

        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)
        return [(top_left, top_right), (top_right, bottom_right),
                    (bottom_right, bottom_left), (bottom_left, top_left)]
    

    def evaluate(self, x):
        if(x > self.rect.right and not self.passed):
            self.passed = True
            return True
        return False
    
    def horizontal_dis(self, x):
        return self.rect.x - x
    
    def intercept(self, x, y):
        return self.rect.left <= x <= self.rect.right and self.rect.top <= y <= self.rect.bottom