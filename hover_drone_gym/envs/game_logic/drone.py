import pygame
from pygame.locals import *
from pygame.sprite import *
import os
from math import sin, cos, pi, radians
import numpy as np

FPS = 60
WIDTH = 800
HEIGHT = 500
BASE_PATH = os.path.realpath("./hover_drone_gym/assets")
DRONE_IMAGE = os.path.join(BASE_PATH, 'drone.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')

class Drone():
    def __init__(self, x, y, screen_width, screen_height, drone_image):
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

    def get_rect_lines(self):
        x, y = self.rect.x, self.rect.y
        w, h = self.rect.width, self.rect.height - 35
        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)

        top_left = self.rotate_point(top_left)
        top_right = self.rotate_point(top_right)
        bottom_left = self.rotate_point(bottom_left)
        bottom_right = self.rotate_point(bottom_right)

        # Return the four lines as tuples (start, end)
        return [(top_left, top_right), (top_right, bottom_right),
                (bottom_right, bottom_left), (bottom_left, top_left)]

    def rotate_point(self, point):
        cx, cy = self.rect.center
        px, py = point

        angle_radian = self.angle * pi / 180
        # Calculate the rotated coordinates
        rotated_x = cx + cos(-angle_radian) * (px - cx) - sin(-angle_radian) * (py - cy)
        rotated_y = cy + sin(-angle_radian) * (px - cx) + cos(-angle_radian) * (py - cy)

        return int(rotated_x), int(rotated_y)
    
    def kia(self):
        self.is_alive = False

    def reset(self):
        self.acceleration_x = 0
        self.acceleration_y = self.gravity
        self.angular_acceleration = 0

    # Rigid body with 2 thrust points
    # The rigid body is shaped like a beam
    # The thrust is directed perpindicular to the beam
    # Two thrust values from -1 to 1 which correlate to the thrusts of each of the 2 thrust points
    # The direction of these thrust values indicates which direction perpindicular to the beam the thrust is going
    # The magnitude of the thrust values correlates to how much thrust is being applied from 0-100%
    def action2(self, thrusts: np.array):
        # constant values
        thrust_value = 1
        air_resistance = 1
        angular_resistance = 1

        # both thrusters are pointing the same direction
        total_thrust = np.sum(thrusts)

        # caclulate thrust direction based on angle
        x_thrust = -(total_thrust * sin(self.angle)) * thrust_value / self.mass
        y_thrust = -(total_thrust * cos(self.angle)) * thrust_value / self.mass

        # calculate angular change based on difference of thrusts
        angle_acc = self.arm * (thrusts[0] - thrusts[1]) * self.arm * thrust_value / self.mass

        x_thrust -= self.velocity_x**2 * self.velocity_x * air_resistance / abs(self.velocity_x)
        y_thrust -= self.velocity_y**2 * self.velocity_y * air_resistance / abs(self.velocity_y)
        angle_acc -= self.angular_speed**2 * self.angular_speed * angular_resistance / abs(self.angular_speed)

        self.velocity_x += self.acceleration_x / FPS
        self.velocity_y += self.acceleration_y / FPS
        self.angular_speed += angle_acc / FPS

    def action(self, key):
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
        elif key==1:
            thruster_left -= self.thruster_amplitude
            thruster_right -= self.thruster_amplitude
        elif key==2:
            thruster_left -= self.diff_amplitude
        elif key==3:
            thruster_right -= self.diff_amplitude
        else:
            self.velocity_x /= 1.01
            self.velocity_y /= 1.05
            self.angle /= 1.001
        
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

        #updating the positions 
        self.rect.y += self.velocity_y
        self.angle += self.angular_speed

        #make it stay on the screen and not move off
        if self.rect.top < 0:
            self.rect.top = 0

def main():
    # Initialize Pygame, load sprites
    FramePerSec = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    image = pygame.image.load(DRONE_IMAGE).convert_alpha()
    drone = Drone(100, int(HEIGHT/2), WIDTH, HEIGHT, image)

    # Game loop
    while True:
        pygame.event.get()

        # Display background
        screen.fill((131, 176, 181))
        
        key = pygame.key.get_pressed()
        drone.action(key)
        drone.update()

        drone.render(screen)

        pygame.display.update()
        FramePerSec.tick(FPS)
    
if __name__=="__main__":
    main()