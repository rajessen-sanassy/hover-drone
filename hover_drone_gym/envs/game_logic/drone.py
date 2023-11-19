import pygame
from pygame.locals import *
from pygame.sprite import *
import os
from math import sin, cos, pi

FPS = 60
WIDTH = 800
HEIGHT = 500
BASE_PATH = os.path.realpath("./hover_drone_gym/assets")
DRONE_IMAGE = os.path.join(BASE_PATH, 'drone.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')

class Drone(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height, drone_image):
        pygame.sprite.Sprite.__init__(self) 
        self.image = drone_image
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

        # physics
        # gravity
        self.gravity = 0.08

        # initialize angular movements
        self.angle = 0
        self.angular_speed = 0
        self.angular_acceleration = 0

        # initialize velocities and accelerations
        self.is_alive = True
        self.screen_width = screen_width
        self.screen_height = screen_height

        # initialize velocities and accelerations
        self.velocity_x = 0
        self.acceleration_x = 0
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

    def action(self, key):
        self.moving = True

        # Resetting values
        self.acceleration_x = 0
        self.acceleration_y = self.gravity
        self.angular_acceleration = 0
        thruster_left = self.thruster_default
        thruster_right = self.thruster_default

        # Adjusting the thrust based on key press
        if key==0:
            thruster_left += self.thruster_amplitude
            thruster_right += self.thruster_amplitude
        if key==1:
            thruster_left -= self.thruster_amplitude
            thruster_right -= self.thruster_amplitude
        if key==2:
            thruster_left -= self.diff_amplitude
        if key==3:
            thruster_right -= self.diff_amplitude
        # else:

        
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
        
        # pygame.transform.rotate(self.image, self.angle)

        #updating the positions 
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

def main():
    # Initialize Pygame, load sprites
    FramePerSec = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    drone_group = pygame.sprite.Group()
    image = pygame.image.load(DRONE_IMAGE).convert_alpha()
    drone = Drone(100, int(HEIGHT/2), WIDTH, HEIGHT, image)
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
        agent_copy = pygame.transform.rotate(drone.image, drone.angle)
        screen.blit(
            agent_copy,
            (
                drone.rect.x,
                drone.rect.y,
            ),
        )

        pygame.display.update()

        pygame.display.update()
        FramePerSec.tick(FPS)
    
if __name__=="__main__":
    main()

def main():
    # Initialize Pygame, load sprites
    FramePerSec = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    drone_group = pygame.sprite.Group()
    image = pygame.image.load(DRONE_IMAGE).convert_alpha()
    drone = Drone(100, int(HEIGHT/2), WIDTH, HEIGHT, image)
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
        agent_copy = pygame.transform.rotate(drone.image, drone.angle)
        screen.blit(
            agent_copy,
            (
                drone.rect.x,
                drone.rect.y,
            ),
        )

        pygame.display.update()

        pygame.display.update()
        FramePerSec.tick(FPS)
    
if __name__=="__main__":
    main()