import pygame
from pygame.locals import *
from pygame.sprite import *
import random
import os

BASE_PATH = os.path.realpath("./hover_drone_gym/assets")
DRONE_IMAGE = os.path.join(BASE_PATH, 'drone.png')
BUILDING_IMAGE = os.path.join(BASE_PATH, 'building.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 800
BUILDING_GAP = 60
SPAWN_RATE_SECONDS = 2
FPS = 60

class Drone(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load(DRONE_IMAGE).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_alive = True
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

    def kia(self):
        self.is_alive = False

    def action(self, key):
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

#creating buildings 
class Building(pygame.sprite.Sprite):
    def __init__(self,x,y,position, building_gap):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(BUILDING_IMAGE).convert_alpha()
        self.rect = self.image.get_rect()
        self.passed = False
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


class HoverDrone():
    def __init__(self):
        pygame.init()
        self.screen_height = SCREEN_HEIGHT
        self.screen_width = SCREEN_WIDTH
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.background = pygame.image.load(BG_IMAGE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_speed = FPS
        self.moving = False
        self.gameover = False
        self.recurr_buildings = SPAWN_RATE_SECONDS*1e3
        self.building_gap = BUILDING_GAP
        self.prev_building = pygame.time.get_ticks()
        self.drone_group = pygame.sprite.Group()
        self.drone = Drone(100, int(self.screen_height/2))
        self.drone_group.add(self.drone)
        self.building_group = pygame.sprite.Group()

    def action(self):
        key = pygame.key.get_pressed()
        
        self.drone.action(key)
        self.drone.update()
        self.check_collision()

    def evaluate(self):
        reward = 0
        for building in self.building_group:
            if building.evaluate(self.drone.rect.x):
                reward += 0.5
        return reward

    def view(self, score):
        for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and self.moving == False and self.gameover == False:
                    if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                        self.moving = True

        self.screen.blit(self.background,(0,0))
        
        self.action()
        self.drone_group.draw(self.screen)
        

        if self.gameover == False and self.moving == True:
            #creating upper and lower buildings
            curr_time = pygame.time.get_ticks()
            if curr_time - self.prev_building > self.recurr_buildings:
                self.create_building()
                self.prev_building = curr_time
        
            #move buidling
            self.building_group.update()
        #draw buidling
        self.building_group.draw(self.screen)

        # score
        text = self.font.render(f"Score: {score}", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width/2, 20)
        self.screen.blit(text, text_rect)

        pygame.display.update()
        self.clock.tick(self.game_speed)

    def create_building(self):
        height_upperbound = (self.screen_height/2)-self.building_gap
        height_lowerbound = (-1)*((self.screen_height/2)-self.building_gap)
        building_height = random.randint(height_lowerbound,height_upperbound)
        lower_building = Building(self.screen_width,int(self.screen_height/2) + building_height, -1, self.building_gap)
        upper_building = Building(self.screen_width,int(self.screen_height/2) + building_height, 1, self.building_gap)
        self.building_group.add(lower_building)
        self.building_group.add(upper_building)
        

    def check_collision(self):
        if pygame.sprite.groupcollide(self.drone_group,self.building_group, False, False) or self.drone.rect.top < 0:
                self.gameover = True
                self.drone.kia()
                return True

    def start(self):
        score = 0
        
        while True:
            if self.check_collision():
                self.reset()

            score += self.evaluate()
            self.view(score)

    def reset(self):
        self.drone.kill()
        self.building_group.empty()
        self.drone_group.empty()

        self.prev_building = pygame.time.get_ticks()
        
        self.drone = Drone(100, int(self.screen_height/2))
        self.drone_group.add(self.drone)

        self.moving = False
        self.gameover = False

        self.start()

def main():
    game = HoverDrone()
    game.start()

if __name__ == '__main__':
    main()