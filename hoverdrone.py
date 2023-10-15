import pygame
from pygame.locals import *
from pygame.sprite import *
from pygame.sprite import *
import random


pygame.init()

screen_height = 500
screen_width = 800

screen = pygame.display.set_mode((screen_width,screen_height))

background = pygame.image.load("whiteBG.jpeg")
#drone = pygame.image.load("Downloads/drone.png")


#rect_1 = drone.get_rect()
#rect_1.center = (200, screen_height/2)


building_gap = 60
moving = False
gameover = False
recurr_buildings = 1500
prev_building = pygame.time.get_ticks()


class Drone(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load("drone.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):

        if gameover:
            return
        key = pygame.key.get_pressed()
        
        #Resetting velocities
        self.velocity_x = 0
        self.velocity_y = 0

        #Adjusting the velocities 
        if key[pygame.K_UP]:
            self.velocity_y = -10
        if key[pygame.K_DOWN]:
            self.velocity_y = 10
        if key[pygame.K_LEFT]:
            self.velocity_x = -10
        if key[pygame.K_RIGHT]:
            self.velocity_x = 10
        
        #updating the velocities 
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        #make it stay on the screen and not move off
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height



drone_group = pygame.sprite.Group()
drones = Drone(100, int(screen_height/2))

drone_group.add(drones)


#creating buildings 
class Building(pygame.sprite.Sprite):
    def __init__(self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("building.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x,y - building_gap]
        if position == -1:
            self.rect.topleft = [x,y + building_gap]
    
    def update(self):
        self.rect.x -= 4
        if self.rect.right < 0:
            self.kill()


building_group = pygame.sprite.Group()


flag = True

while flag:
    pygame.time.delay(20)

    screen.blit(background,(0,0))

    building_group.draw(screen)

    drone_group.draw(screen)
    drone_group.update()

    if pygame.sprite.groupcollide(drone_group,building_group, False, False) or drones.rect.top < 0:
        gameover = True


    #creating upper and lower buildings and making them move
    if gameover == False and moving == True:
        curr_time = pygame.time.get_ticks()
        if curr_time - prev_building > recurr_buildings:
            building_height = random.randint(-100,100)
            lower_building = Building(screen_width,int(screen_height/2) + building_height,-1)
            upper_building = Building(screen_width,int(screen_height/2)+ building_height ,1)
            building_group.add(lower_building)
            building_group.add(upper_building)
            prev_building = curr_time
        
        building_group.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
        if event.type == pygame.KEYDOWN and moving == False and gameover == False:
            if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                moving = True


    pygame.display.update()


pygame.quit()

