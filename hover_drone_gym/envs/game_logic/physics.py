import numpy as np
from math import sin, cos, pi

class Physics():
    def __init__(self, action_space_type):
        self._action_space_type = action_space_type

        # gravity
        self._gravity = 0.08

        # initialize angular movements
        self._angle = 0
        self._angular_speed = 0
        self._angular_acceleration = 0

        # initialize velocities and accelerations
        self._velocity_x = 0
        self._velocity_y = 0
        self._acceleration_x = 0
        self._acceleration_y = 0

        # propeller thrust to be added upon button presses
        self._thruster_amplitude = 0.04

        # rate of rotation upon button presses
        self._diff_amplitude = 0.003

        # Default propeller force
        self._thruster_default = 0.04

        self._mass = 1

        # Length from center of mass to propeller
        self._arm = 25

        # Test
    
    def move(self, action):
        if(self._action_space_type=="discrete"):
            self._discrete_action(action)
        elif(self._action_space_type=="continuous"):
            # self._continous_action(action)
            self._test_continuous_action(action)

        self._angle += self._angular_speed

        return self._velocity_x, self._velocity_y
    
    def _test_continuous_action(self, thrusts: np.array):
        (action0, action1) = (thrusts[0], thrusts[1])

        self._acceleration_x = 0
        self._acceleration_y = self._gravity
        self._angular_acceleration = 0
        thruster_left = self._thruster_default
        thruster_right = self._thruster_default

        thruster_left += action0 * self._thruster_amplitude
        thruster_right += action0 * self._thruster_amplitude
        thruster_left += action1 * self._diff_amplitude
        thruster_right -= action1 * self._diff_amplitude

        self._acceleration_x += (-(thruster_left + thruster_right) * sin(self.angle * pi / 180) / self._mass)
        self._acceleration_y += (-(thruster_left + thruster_right) * cos(self.angle * pi / 180) / self._mass)
        self._angular_acceleration += self._arm * (thruster_right - thruster_left) / self._mass

        self._velocity_x += self._acceleration_x
        self._velocity_y += self._acceleration_y
        self._angular_speed += self._angular_acceleration

    # Rigid body with 2 thrust points
    # The rigid body is shaped like a beam
    # The thrust is directed perpindicular to the beam
    # Two thrust values from -1 to 1 which correlate to the thrusts of each of the 2 thrust points
    # The direction of these thrust values indicates which direction perpindicular to the beam the thrust is going
    # The magnitude of the thrust values correlates to how much thrust is being applied from 0-100%
    def _continous_action(self, thrusts: np.array):
        # constant values
        thrust_value = 1
        air_resistance = 1
        angular_resistance = 1

        # prevent 0 division error
        self._velocity_x += 1e-5
        self._velocity_y += 1e-5
        self._angular_speed += 1e-5

        # both thrusters are pointing the same direction
        total_thrust = np.sum(thrusts)

        # caclulate thrust direction based on angle
        x_thrust = -(total_thrust * sin(self._angle)) * thrust_value / self._mass
        y_thrust = -(total_thrust * cos(self._angle)) * thrust_value / self._mass

        # calculate angular change based on difference of thrusts
        angle_acc = self._arm * (thrusts[0] - thrusts[1]) * self._arm * thrust_value / self._mass

        x_thrust -= self._velocity_x**2 * self._velocity_x * air_resistance / abs(self._velocity_x)
        y_thrust -= self._velocity_y**2 * self._velocity_y * air_resistance / abs(self._velocity_y)
        angle_acc -= self._angular_speed**2 * self._angular_speed * angular_resistance / abs(self._angular_speed)

        self._velocity_x += self._acceleration_x
        self._velocity_y += self._acceleration_y 
        self._angular_speed += angle_acc

    def _discrete_action(self, key):
        # Resetting values
        self._acceleration_x = 0
        self._acceleration_y = self._gravity
        self._angular_acceleration = 0
        thruster_left = self._thruster_default
        thruster_right = self._thruster_default

        # Adjusting the thrust based on key press
        if key==0:
            thruster_left += self._thruster_amplitude
            thruster_right += self._thruster_amplitude
        elif key==1:
            thruster_left -= self._thruster_amplitude
            thruster_right -= self._thruster_amplitude
        elif key==2:
            thruster_left -= self._diff_amplitude
        elif key==3:
            thruster_right -= self._diff_amplitude
        else:
            self._velocity_x /= 1.01
            self._velocity_y /= 1.05
            self._angle /= 1.001
        
        total_thrust = thruster_left + thruster_right
        angle_radian = self.angle * pi / 180

        # calculate x y acceleration based on angle
        self._acceleration_x += (-(total_thrust) * sin(angle_radian) / self._mass)
        self._acceleration_y += (-(total_thrust) * cos(angle_radian) / self._mass)

        # negative = right rotation in pygame
        self._angular_acceleration += self._arm * (thruster_right - thruster_left) / self._mass

        # update velocities
        self._velocity_x += self._acceleration_x
        self._velocity_y += self._acceleration_y
        self._angular_speed += self._angular_acceleration

    @property
    def angle(self): 
        return self._angle
    
    @property
    def angular_speed(self): 
        return self._angular_speed