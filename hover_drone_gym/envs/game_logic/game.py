import pygame
from hover_drone_gym.envs.utils import load_images
from pygame.locals import *
from pygame.sprite import *
import random
from hover_drone_gym.envs.game_logic.drone import Drone
from hover_drone_gym.envs.game_logic.building import Building
from math import sqrt, cos, sin, pi, pow
import numpy as np

class Game():
    def __init__(self, screen_size, building_gap, spawn_rate, FPS):
        pygame.init()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.SysFont('hover_drone_gym/assets/custom_font.ttf', 30)
        images = load_images()
        self.background = images["background"]
        self.drone_image = images["drone_1"]
        self.drone_image2 = images["drone_2"]
        self.building_image = images["building"]
        self.game_speed = FPS
        self.moving = False
        self.gameover = False
        self.recurr_buildings = spawn_rate
        self.building_gap = building_gap
        self.prev_building = None                            
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.drone_image)
        self.building_group = []
        self.score = 0
        self.step = 0
        self.radars = [(0,0) * 5]

    def get_raycast(self):
        return np.array([raycast[1] for raycast in self.radars])

    def get_velocity(self):
        # velocity = sqrt(self.drone.velocity_x**2 + self.drone.velocity_y**2)

        return np.array([self.drone.velocity_x, self.drone.velocity_y])

    def get_angle(self): return self.drone.angle

    def get_angle_velocity(self): return self.drone.angular_speed

    def check_building_intercept(self, x, y):
        for buildings in self.building_group:
            for building in buildings:
                if building.intercept(x, y):
                    return True
        return False
    
    def check_screen_intercept(self, x, y):
        if(y == 0 or y == self.screen_height):
            return True
        return False

    def check_radar(self, degree):
        length = 0
        center = [self.drone.rect.center[0], self.drone.rect.center[1]-18]
        angle_radian = degree * pi / 180
        x = int(center[0] + cos(angle_radian) * length)
        y = int(center[1] + sin(angle_radian) * length)

        while not (self.check_building_intercept(x, y) or self.check_screen_intercept(x, y)) \
            and length < (self.screen_width - self.drone.rect.center[0]):
            length = length + 1
            x = int(center[0] + cos(angle_radian) * length)
            y = int(center[1] + sin(angle_radian) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(sqrt(pow(x - center[0], 2) + pow(y - center[1], 2)))
        self.radars.append([(x, y), dist])

    def distance_to_target(self):
        target = self.get_target()
        if not target:
            return 0

        point1 = (self.drone.rect.center[0], self.drone.rect.center[1]-18)
        point2 = target[1]

        # if(point1[0] > point2[0]):
        #     return 0

        return int(sqrt(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2)))

    def get_target(self):
        for buildings in self.building_group:
            if(not buildings[0].passed):
                building_top = buildings[1].get_rect_lines()
                building_bottom = buildings[0].get_rect_lines()
                
                return [building_top[2], (building_top[1][1], building_bottom[1][0]),
                    building_bottom[0], (building_bottom[0][0], building_top[3][0])], \
                    (building_bottom[0][1][0], int((building_top[3][0][1] + building_bottom[0][0][1])/2))
        
        return False

    def check_collisions(self):
        # check building collision
        for buildings in self.building_group:
            for building in buildings:
                building_lines = building.get_rect_lines()
                if self.check_hitbox(building_lines):
                    self.drone.kia()
                    return True

        # check ground and ceiling collision
        floor_line = [((0, self.screen_height), (self.screen_width, self.screen_height)) * 4]
        ceiling_line = [((0, 0), (self.screen_width, 0)) * 4]
        if self.check_hitbox(floor_line) or self.check_hitbox(ceiling_line):
            self.drone.kia()
            return True

        return False
    
    def check_hitbox(self, building_lines):
        drone_lines = self.drone.get_rect_lines()

        for line1 in drone_lines:
            for line2 in building_lines:
                if self.are_lines_intersecting(line1, line2):
                    return True
        return False
    
    def are_lines_intersecting(self, line1, line2):
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if den == 0:
            return False  # Lines are parallel or coincident

        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

        return 0 <= ua <= 1 and 0 <= ub <= 1


    def update_state(self, action):
        self.moving = True      
        self.drone.action(action)
        self.drone.update()
        self.evaluate()

        self.radars.clear()
        degrees = [-90, -45, -30, -15, 0, 15, 30, 45, 90]
        for degree in degrees:
            self.check_radar(degree)

        return self.check_collisions()
        
    def evaluate(self):
        for buildings in self.building_group:
            if buildings[0].evaluate(self.drone.rect.center[0]):
                    buildings[1].is_passed = True
                    self.score += 1
                    return True
        return False
    
    def view(self):
        self.screen.blit(self.background,(0,0))
        
        if self.gameover == False and self.moving == True:
            #creating upper and lower buildings
            if not self.prev_building or self.prev_building.rect.x < (self.screen_width - self.recurr_buildings):
                self.prev_building = self.create_building()
            
            #move buidling
            for buildings in self.building_group:
                for building in buildings:
                    building_speed = max(int(self.drone.velocity_x), 0)
                    building.rect.x -= building_speed
                    if building.rect.right < 0:
                        building.kill()
                    #draw buidling
                    self.screen.blit(building.image, (building.rect.x, building.rect.y))

        # score
        text = self.font.render(f"Score: {self.score}", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width/2, 20)
        self.screen.blit(text, text_rect)

        # update drone
        self.step += 1
        if(int(self.step * 0.3) % 2):
            player_sprite = self.drone_image
        else:
            player_sprite = self.drone_image2

        player_copy = pygame.transform.rotate(player_sprite, self.drone.angle)
        rotated_rect = player_copy.get_rect(center=self.drone.rect.center)
        draw_pos = rotated_rect.topleft
        # Blit the rotated image at the new position
        self.screen.blit(player_copy, draw_pos)

        if self.gameover == False and self.moving == True: 
            drone_position = (self.drone.rect.center[0], self.drone.rect.center[1]-18)
            for radar in self.radars:
                position = radar[0]
                pygame.draw.line(self.screen, (0, 255, 0), drone_position, position, 1)
                pygame.draw.circle(self.screen, (0, 255, 0), position, 5)
            
            target = self.get_target()
            for line in target[0]:
                pygame.draw.line(self.screen, (0, 0, 255), line[0], line[1], 1)
            
            pygame.draw.line(self.screen, (0, 0, 255), drone_position, target[1], 1)
            pygame.draw.circle(self.screen, (0, 0, 255), target[1], 5)



        for line in self.drone.get_rect_lines():
            pygame.draw.line(self.screen, (255, 0, 0), line[0], line[1])

        pygame.display.update()
        self.clock.tick(self.game_speed)

    def create_building(self):
        height_upperbound = (self.screen_height/2)-self.building_gap
        height_lowerbound = (-1)*((self.screen_height/2)-self.building_gap)
        building_height = random.randint(height_lowerbound,height_upperbound)
        lower_building = Building(self.screen_width,int(self.screen_height/2) + building_height, -1, self.building_gap, self.building_image)
        upper_building = Building(self.screen_width,int(self.screen_height/2) + building_height, 1, self.building_gap, self.building_image)
        self.building_group.append((lower_building, upper_building))
        return lower_building

    def action(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not self.moving and not self.gameover:
                if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                    self.moving = True

        if (self.moving):
            key = pygame.key.get_pressed()

            if key[pygame.K_UP]:
                key = 0
            elif key[pygame.K_DOWN]:
                key = 1
            elif key[pygame.K_LEFT]:
                key = 2
            elif key[pygame.K_RIGHT]:
                key = 3

            self.update_state(key)

    def _get_obs(self):
        return {
            'distance_to_target': self.distance_to_target(),
            'raycast': self.get_raycast(),
            'velocity': self.get_velocity(),
            'angle': [self.get_angle()],
            'angle_velocity': [self.get_angle_velocity()],
        }

    def start(self):
        while True:    
            if not self.drone.is_alive:
                self.reset()

            self.action()
            self.view()
            print(self._get_obs())

    def reset(self):
        self.score = 0
        self.step = 0
        self.drone = None
        self.building_group = []
        self.radars = [(0,0) * 5]

        self.prev_building = None
        
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.drone_image)
        
        self.moving = False
        self.gameover = False