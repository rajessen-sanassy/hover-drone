import pygame
from pygame.locals import *
from pygame.sprite import *

class Drone(pygame.sprite.Sprite):
    def __init__(self,x,y, sw, hs, images):
        pygame.sprite.Sprite.__init__(self) 
        self.image = images["drone"]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_alive = True
        self.screen_width = sw
        self.screen_height = hs

    def kia(self):
        self.is_alive = False

    def action(self, key):
        self.moving = True
        #Resetting velocities
        self.velocity_x = 0
        self.velocity_y = 0

        #Adjusting the velocities 
        if key==0:
            self.velocity_y = -10
        if key==1:
            self.velocity_y = 10
        if key==2:
            self.velocity_x = -10
        if key==3:
            self.velocity_x = 10

    def update(self):
        if(not self.is_alive):
            return
        
        #updating the velocities 
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        #make it stay on the screen and not move off
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height