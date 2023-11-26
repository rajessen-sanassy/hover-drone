
import pygame
from hover_drone_gym.envs.utils import load_images

class Render():
    def __init__(self, screen_size, screen_height, drone_image):
        pygame.init()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.clock = pygame.time.Clock()
        self.game_speed = FPS
        pygame.display.set_caption('Hover Drone')
        self.font = pygame.font.SysFont('hover_drone_gym/assets/custom_font.ttf', 30)
        images = load_images()
        self.background = images["background"]
        self.drone_image = images["drone_1"]
        self.drone_image2 = images["drone_2"]
        self.building_image = images["building"]

    def get_screen_width(self): return self.screen_width

    def get_screen_height(self): return self.screen_height

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

        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(self.screen, (0, 255, 0), (self.drone.rect.center[0], self.drone.rect.center[1]-18) , position, 1)
            pygame.draw.circle(self.screen, (0, 255, 0), position, 5)

        for line in self.drone.get_rect_lines():
            pygame.draw.line(self.screen, (255, 0, 0), line[0], line[1])

        pygame.display.update()
        self.clock.tick(self.game_speed)