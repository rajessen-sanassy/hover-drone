import pygame
from pygame.locals import *
from pygame.sprite import *
import os
from math import sin, cos, pi

FPS = 60
WIDTH = 800
HEIGHT = 800
BASE_PATH = os.path.realpath("./hover_drone_gym/assets")
DRONE_IMAGE = os.path.join(BASE_PATH, 'drone.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')

class Drone(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load(DRONE_IMAGE).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.is_alive = True
        self.screen_width = screen_width
        self.screen_height = screen_height

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
        self.thruster_mean = 0.04
        self.mass = 1

        # Length from center of mass to propeller
        self.arm = 25

    def kia(self):
        self.is_alive = False

    def action(self, key):
        self.moving = True

        # Resetting values
        self.acceleration_x = 0
        self.acceleration_y = self.gravity
        self.angular_acceleration = 0
        thruster_left = self.thruster_mean
        thruster_right = self.thruster_mean

        # Adjusting the velocities 
        if key[K_UP]:
            thruster_left += self.thruster_amplitude
            thruster_right += self.thruster_amplitude
        if key[K_DOWN]:
            thruster_left -= self.thruster_amplitude
            thruster_right -= self.thruster_amplitude
        if key[K_LEFT]:
            thruster_left -= self.diff_amplitude
        if key[K_RIGHT]:
            thruster_right -= self.diff_amplitude
        
        self.acceleration_x += (-(thruster_left + thruster_right) * sin(self.angle * pi / 180) / self.mass)
        self.acceleration_y += (-(thruster_left + thruster_right) * cos(self.angle * pi / 180) / self.mass)
        self.angular_acceleration += self.arm * (thruster_right - thruster_left) / self.mass

        self.velocity_x += self.acceleration_x
        self.velocity_y += self.acceleration_y
        self.angular_speed += self.angular_acceleration

    def update(self):
        if(not self.is_alive):
            return
        
        pygame.transform.rotate(self.image, self.angle)

        #updating the velocities 
        self.rect.x += self.velocity_x
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

def main():
    # Initialize Pygame, load sprites
    FramePerSec = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    drone_group = pygame.sprite.Group()
    drone = Drone(100, int(HEIGHT/2), WIDTH, HEIGHT)
    drone_group.add(drone)

    # Game loop
    while True:
        pygame.event.get()

        # Display background
        screen.fill((131, 176, 181))
        
        key = pygame.key.get_pressed()
        drone.action(key)
        drone.update()

        # rotate drone sprite according to the current calculation of the rotation
        player_copy = pygame.transform.rotate(drone.image, drone.angle)
        screen.blit(
            player_copy,
            (
                drone.rect.x - int(player_copy.get_width() / 2),
                drone.rect.y - int(player_copy.get_height() / 2),
            ),
        )

        pygame.display.update()

        pygame.display.update()
        FramePerSec.tick(FPS)
    
if __name__=="__main__":
    main()