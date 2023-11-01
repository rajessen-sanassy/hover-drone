import pygame
from hover_drone_gym.envs.utils import load_images
from pygame.locals import *
from pygame.sprite import *
import random
from hover_drone_gym.envs.game_logic.drone import Drone
from hover_drone_gym.envs.game_logic.building import Building
from math import tan

class HoverDrone:
    def __init__(self, screen_size, building_gap, spawn_rate, FPS):
        pygame.init()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.SysFont("Arial", 30)
        images = load_images()
        self.background = images["background"]
        self.drone_image = images["drone_1"]
        self.drone_image2 = images["drone_2"]
        self.building_image = images["building"]
        self.game_speed = FPS
        self.moving = False
        self.gameover = False
        self.recurr_buildings = spawn_rate*1e3
        self.building_gap = building_gap
        self.prev_building = pygame.time.get_ticks()
        self.drone_group = pygame.sprite.Group()                                       
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.drone_image)
        self.drone_group.add(self.drone)
        self.building_group = pygame.sprite.Group()
        self.score = 0
        self.step = 0

    def get_velocity_vector(self):
        speed = ((self.drone.velocity_x)**2 + (self.drone.velocity_y)**2)**(1/2)
        angle = tan(self.drone.velocity_y / (self.drone.velocity_x + 0.00001))

        return speed, angle

    # angle_to_up
    def get_angle(self): return self.drone.angle

    def get_angle_to_target(self):
        # TODO: ASK JOSH ABOUT ANGLES, WHERE IS 0, CLOCKWISE OR COUNTERCLOCKWISE, RADIANS OR DEGREES
        dis_to_target = self.y_distance_from_safe_zone()

        # if below safe zone, angle to target is 0 (also 0 if drone is inside safe zone)
        if dis_to_target <= 0:
            angle_to_target = 0
        # if above safe zone, angle to target is 180
        else:
            angle_to_target = 180

        return abs(angle_to_target - self.drone.angle)

    # TODO: Not needed?
    def get_angle_velocity(self):
        return self.get_velocity_vector()[1]

    # angle_target_and_velocity
    def get_velocity_angle_to_target(self):
        dis_to_target = self.y_distance_from_safe_zone()

        # if below safe zone, angle to target is 0 (also 0 if drone is inside safe zone)
        if dis_to_target <= 0:
            angle_to_target = 0
        # if above safe zone, angle to target is 180
        else:
            angle_to_target = 180

        return abs(angle_to_target - self.get_velocity_vector()[1])

    def update_state(self, action):
        self.moving = True      
        self.drone.action(action)
        self.drone.update()
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
        
        return safe_zone_top_left, safe_zone_bottom_right


    def y_distance_from_safe_zone(self):
        safe_zone = self.safe_zone()
        if safe_zone == None:
            return 0
        safe_zone_topleft, safe_zone_bottomright = safe_zone

        if safe_zone_topleft[1] <= self.drone.rect.y:
            if self.drone.rect.bottomright[1] <= safe_zone_bottomright[1]: # drone is in safe zone
                return 0
            
            # drone is below safe zone
            return safe_zone_bottomright[1] - self.drone.rect.bottomright[1]
        
        # drone is above safe zone
        return safe_zone_topleft[1] - self.drone.rect.y
        

    def evaluate(self):
        score = 0
        for building in self.building_group:
            if building.evaluate(self.drone.rect.x):
                score += 0.5
        return score

    def view(self):
        self.screen.blit(self.background,(0,0))
        
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

        # update drone
        self.step += 1
        print(int(self.step * 0.3) % 2)
        if(int(self.step * 0.3) % 2):
            player_sprite = self.drone_image
        else:
            player_sprite = self.drone_image2

        player_copy = pygame.transform.rotate(player_sprite, self.drone.angle)
        self.screen.blit(
            player_copy,
            (
                self.drone.rect.x,
                self.drone.rect.y,
            ),
        )

        pygame.display.update()
        self.clock.tick(self.game_speed)

    def create_building(self):
        height_upperbound = (self.screen_height/2)-self.building_gap
        height_lowerbound = (-1)*((self.screen_height/2)-self.building_gap)
        building_height = random.randint(height_lowerbound,height_upperbound)
        lower_building = Building(self.screen_width,int(self.screen_height/2) + building_height, -1, self.building_gap, self.building_image)
        upper_building = Building(self.screen_width,int(self.screen_height/2) + building_height, 1, self.building_gap, self.building_image)
        self.building_group.add(lower_building)
        self.building_group.add(upper_building)
        

    def check_collision(self):
        if pygame.sprite.groupcollide(self.drone_group,self.building_group, False, False) or self.drone.rect.top < 0:
                self.gameover = True
                self.drone.kia()
                return True

        if(self.drone.rect.y >= self.screen_height-self.drone.image.get_height()):
            return True

        return False

    def reset(self):
        self.score = 0
        self.step = 0
        self.drone.kill()
        self.building_group.empty()
        self.drone_group.empty()

        self.prev_building = pygame.time.get_ticks()
        
        self.drone = Drone(100, int(self.screen_height/2), self.screen_width, self.screen_height, self.drone_image)
        self.drone_group.add(self.drone)

        self.moving = False
        self.gameover = False