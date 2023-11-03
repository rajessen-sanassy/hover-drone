import pygame
from pygame.locals import *
from pygame.sprite import *
import random
import os
from math import sin, cos, pi

BASE_PATH = os.path.realpath("./hover_drone_gym/assets")
DRONE_IMAGE1 = os.path.join(BASE_PATH, 'drone_1.png')
DRONE_IMAGE2 = os.path.join(BASE_PATH, 'drone_2.png')
BUILDING_IMAGE = os.path.join(BASE_PATH, 'building.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 800
BUILDING_GAP = 80
SPAWN_RATE_SECONDS = 4
FPS = 60

class Drone(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load(DRONE_IMAGE1).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_alive = True
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # physics
        # gravity
        self.gravity = 0.08

        # initialize angular movements
        self.angle = 0
        self.angular_speed = 0
        self.angular_acceleration = 0

        # initialize velocities and accelerations
        self.velocity_x = 0
        self.acceleration_x = 0
        self.velocity_y = 0
        self.acceleration_y = 0

        # propeller thrust to be added upon button presses
        self.thruster_amplitude = 0.04

        # rate of rotation upon button presses
        self.diff_amplitude = 0.003

        # Default propeller force
        self.thruster_default = 0.04

        self.mass = 1

        # Length from center of mass to propeller
        self.arm = 25

    def kia(self):
        self.is_alive = False

    def reset(self):
        self.acceleration_x = 0
        self.acceleration_y = self.gravity
        self.angular_acceleration = 0

    def action(self, key):
        # Resetting values
        self.reset()
        thruster_left = self.thruster_default
        thruster_right = self.thruster_default

        # Adjusting the thrust based on key press
        if key[pygame.K_UP]:
            thruster_left += self.thruster_amplitude
            thruster_right += self.thruster_amplitude
        if key[pygame.K_DOWN]:
            thruster_left -= self.thruster_amplitude
            thruster_right -= self.thruster_amplitude
        if key[pygame.K_LEFT]:
            thruster_left -= self.diff_amplitude
        if key[pygame.K_RIGHT]:
            thruster_right -= self.diff_amplitude
        
        total_thrust = thruster_left + thruster_right
        angle_radian = self.angle * pi / 180

        # calculate x y acceleration based on angle
        self.acceleration_x += (-(total_thrust) * sin(angle_radian) / self.mass)
        self.acceleration_y += (-(total_thrust) * cos(angle_radian) / self.mass)

        # negative = right rotation in pygame
        self.angular_acceleration += self.arm * (thruster_right - thruster_left) / self.mass

        # update velocities
        self.velocity_x += self.acceleration_x
        self.velocity_y += self.acceleration_y
        self.angular_speed += self.angular_acceleration

    def update(self):
        if(not self.is_alive):
            return

        # #updating the positions 
        # self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.angle += self.angular_speed

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
        self.pos = position
        self.passed = False
        self.building_gap = building_gap

        if position == 1:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x,y - self.building_gap]
        if position == -1:
            self.rect.topleft = [x,y + self.building_gap]
    
    def evaluate(self, x):
        if(x > self.rect.bottomright[0] and not self.passed):
            self.passed = True
            return True
        return False
    
    def horizontal_dis(self, x):
        return self.rect.x - x


class Game():
    def __init__(self):
        pygame.init()
        self.screen_height = SCREEN_HEIGHT
        self.screen_width = SCREEN_WIDTH
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.background = pygame.image.load(BG_IMAGE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.Font('hover_drone_gym/assets/custom_font.ttf', 30)
        self.game_speed = FPS
        self.moving = False
        self.gameover = False
        self.recurr_buildings = 400
        self.building_gap = BUILDING_GAP
        self.prev_building = None
        self.drone_group = pygame.sprite.Group()
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height)
        self.drone_group.add(self.drone)
        self.building_group = pygame.sprite.Group()

    def has_moved(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not self.moving and not self.gameover:
                if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                    return True

    def action(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not self.moving and not self.gameover:
                if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                    self.moving = True
    
        if (self.moving):
            key = pygame.key.get_pressed()
            self.drone.action(key)
            self.drone.update()
            self.check_collision()

    def evaluate(self):
        score = 0
        for building in self.building_group:
            if building.evaluate(self.drone.rect.x):
                score += 0.5
        return int(score)

    def view(self, score, step):
        self.screen.blit(self.background,(0,0))
        self.safe_zone()
        # self.drone_group.draw(self.screen)

        if self.gameover == False and self.moving == True:
            #creating upper and lower buildings
            if not self.prev_building or self.prev_building.rect.x < (self.screen_width - self.recurr_buildings):
                self.prev_building = self.create_building()
        
            #move buidling
            for building in self.building_group:
                building_speed = max(int(self.drone.velocity_x), 0)
                building.rect.x -= building_speed
                if building.rect.right < 0:
                    building.kill()
                #draw buidling
                self.screen.blit(building.image, (building.rect.x, building.rect.y))
            
        # #draw buidling
        # self.building_group.draw(self.screen)

        # score
        text = self.font.render(f"Score: {score}", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width/2, 20)
        self.screen.blit(text, text_rect)

        #update drone
        images = [pygame.image.load(DRONE_IMAGE1).convert_alpha(), pygame.image.load(DRONE_IMAGE2).convert_alpha()]
        player_sprite = images[int(step * 0.3) % 2]
        player_copy = pygame.transform.rotate(player_sprite, self.drone.angle)
        self.screen.blit(
            player_copy,
            (
                100,
                self.drone.rect.y + 30,
            ),
        )

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
        return lower_building # keep track of last building

    def check_collision(self):
        if pygame.sprite.groupcollide(self.drone_group,self.building_group, False, False) or self.drone.rect.top < 0:
                self.gameover = True
                self.drone.kia()
                return True

        if(self.drone.rect.y >= self.screen_height-self.drone.image.get_height()):
            return True
        return False

    def safe_zone(self):
        min_horizontal_dis = float('inf')
        building_1 = None
        building_2 = None

        if len(self.building_group) == 0: # return if there are no buildings
            return

        all_buildings_passed = True

        for building in self.building_group:
            if building.passed: # if the drone is already passed the building, we ignore it
                continue
            
            all_buildings_passed = False

            dis = building.horizontal_dis(self.drone.rect.x)

            if dis < min_horizontal_dis:
                min_horizontal_dis = dis
                building_1 = building

        if all_buildings_passed:
            return

        for building in self.building_group:
            if building.rect.x == building_1.rect.x and building.pos == (building_1.pos * -1):
                building_2 = building

        if building_1.rect.y < building_2.rect.y:
            safe_zone_top_left = [0, building_1.rect.bottomleft[1]]
            safe_zone_bottom_right = building_2.rect.topright
        else:
            safe_zone_top_left = [0, building_2.rect.bottomleft[1]]
            safe_zone_bottom_right = building_1.rect.topright
        
        width = safe_zone_bottom_right[0]
        height = safe_zone_top_left[1] - safe_zone_bottom_right[1]

        # rectangle_color = (0, 255, 0)
        # pygame.draw.rect(self.screen, rectangle_color, (safe_zone_top_left[0], safe_zone_top_left[1], width, height))
        return safe_zone_top_left, safe_zone_bottom_right

    def start(self):
        score = 0
        step = 0
        while True:
            step += 1
            # if(not self.moving):
            #     self.moving = self.has_moved()
    
            if self.check_collision():
                self.reset()
            score += self.evaluate()
            self.view(score, step)
            self.action()

    def reset(self):
        self.drone.kill()
        self.building_group.empty()
        self.drone_group.empty()

        self.prev_building = None
        
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height)
        self.drone_group.add(self.drone)

        self.moving = False
        self.gameover = False

        self.start()

def main():
    game = Game()
    game.start()

if __name__ == '__main__':
    main()