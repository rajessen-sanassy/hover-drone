import pygame
from hover_drone_gym.envs.utils import load_images
from pygame.locals import *
from pygame.sprite import *
import random
from hover_drone_gym.envs.game_logic.drone import Drone
from hover_drone_gym.envs.game_logic.building import Building

class HoverDrone:
    def __init__(self, screen_size, building_gap, spawn_rate, FPS):
        pygame.init()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.SysFont("Arial", 30)
        self.images = load_images()
        self.background = self.images["background"]
        self.game_speed = FPS
        self.moving = False
        self.gameover = False
        self.recurr_buildings = spawn_rate*1e3
        self.building_gap = building_gap
        self.prev_building = pygame.time.get_ticks()
        self.drone_group = pygame.sprite.Group()
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.images)
        self.drone_group.add(self.drone)
        self.building_group = pygame.sprite.Group()
        self.score = 0

    def update_state(self, action):
        self.moving = True      
        self.drone.action(action)
        self.drone.update()
        self.score += self.evaluate()
        return self.check_collision()

    def nearest_building(self):
        min_horizontal_dis = float('inf')
        dis = 0
        rectX = 0
        pos = 0
        y1 = 0
        y2 = 0

        for building in self.building_group:
            dis = building.horizontal_dis(self.drone.rect.x)
            if dis >= 0 and dis < min_horizontal_dis:
                min_horizontal_dis = dis
                rectX = building.rect.x
                y1 = building.rect.y
                pos = building.pos

        for x in self.building_group:
            if x.rect.x == rectX and x.pos == (pos * -1):
                y2 = x.rect.y

        y_diff = self.drone.rect.y - (y1 + y2 / 2)

        return dis, y_diff


    def evaluate(self):
        reward = 0
        for building in self.building_group:
            if building.evaluate(self.drone.rect.x):
                reward += 0.5
        return reward

    def view(self):
        self.screen.blit(self.background,(0,0))
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
        text = self.font.render(f"Score: {self.score}", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width/2, 20)
        self.screen.blit(text, text_rect)

        pygame.display.update()
        self.clock.tick(self.game_speed)

    def create_building(self):
        height_upperbound = (self.screen_height/2)-self.building_gap
        height_lowerbound = (-1)*((self.screen_height/2)-self.building_gap)
        building_height = random.randint(height_lowerbound,height_upperbound)
        lower_building = Building(self.screen_width,int(self.screen_height/2) + building_height, -1, self.building_gap, self.images)
        upper_building = Building(self.screen_width,int(self.screen_height/2) + building_height, 1, self.building_gap, self.images)
        self.building_group.add(lower_building)
        self.building_group.add(upper_building)
        

    def check_collision(self):
        if pygame.sprite.groupcollide(self.drone_group,self.building_group, False, False) or self.drone.rect.top < 0:
                self.gameover = True
                self.drone.kia()
                return True

    def reset(self):
        self.score = 0
        self.drone.kill()
        self.building_group.empty()
        self.drone_group.empty()

        self.prev_building = pygame.time.get_ticks()
        
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.images)
        self.drone_group.add(self.drone)

        self.moving = False
        self.gameover = False