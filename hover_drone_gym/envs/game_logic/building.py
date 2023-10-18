import pygame
from pygame.locals import *
from pygame.sprite import *

#creating buildings 
class Building(pygame.sprite.Sprite):
    def __init__(self,x,y,position, building_gap, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["building"]
        self.rect = self.image.get_rect()
        self.passed = False
        self.pos = position
        self.building_gap = building_gap

        if position == 1:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x,y - self.building_gap]
        if position == -1:
            self.rect.topleft = [x,y + self.building_gap]
    
    def evaluate(self, x):
        if(x > self.rect.x and not self.passed):
            self.passed = True
            return True
        return False
    
    def horizontal_dis(self, x):
        return self.rect.x - x

    def update(self):
        self.rect.x -= 4
        if self.rect.right < 0:
            self.kill()