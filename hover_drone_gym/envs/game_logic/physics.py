import numpy as np
from math import sin, cos, pi

class Physics():
    def __init__(self, action_space_type):
        """
        Initialize the Physics object.

        Parameters:
            - action_space_type: A string indicating the type of action space, either "discrete" or "continuous".
        """
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
    
    def move(self, action) -> (float, float):
        """
        Move the drone based on the given action.

        Parameters:
            - action: Action to be applied.

        Returns:
            The updated velocity along the x-axis and y-axis.
        """
        if(self._action_space_type=="discrete"):
            self._discrete_action(action)
        elif(self._action_space_type=="continuous"):
            self._continous_action(action)

        self._angle += self._angular_speed

        return self._velocity_x, self._velocity_y
    
    def _continous_action(self, factors: np.array) -> None:
        """
        Move the drone in a continuous action space based on given factors.

        Parameters:
            - factors: An array representing the factors for continuous actions (-1 to 1).
        """
        # factor0 = overall thrusts on thrusters
        # factor1 = rotational thrust
        (factor0, factor1) = (factors[0], factors[1])
        thrust_value = 1
        air_resistance = 1
        angular_resistance = 1

        # reset thrusts to default values
        thruster_left = self._thruster_default
        thruster_right = self._thruster_default

        # reset drone accelerations
        self._acceleration_x = 0
        self._acceleration_y = self._gravity
        self._angular_acceleration = 0

        # calculate thrust based on thrust factor inputs (factor0, factor1)
        thruster_left += factor0 * self._thruster_amplitude * thrust_value
        thruster_right += factor0 * self._thruster_amplitude * thrust_value

        # adjust thrusts based on factor1 for turning
        thruster_left += factor1 * self._diff_amplitude
        thruster_right -= factor1 * self._diff_amplitude

        # calculate accelerations based on thrust
        self._acceleration_x += (-(thruster_left + thruster_right) * sin(self.angle * pi / 180) / (self._mass * air_resistance))
        self._acceleration_y += (-(thruster_left + thruster_right) * cos(self.angle * pi / 180) / (self._mass * air_resistance))
        self._angular_acceleration += self._arm * (thruster_right - thruster_left) / (self._mass  * angular_resistance)

        # update velocity
        self._velocity_x += self._acceleration_x
        self._velocity_y += self._acceleration_y
        self._angular_speed += self._angular_acceleration

    def _discrete_action(self, key: int) -> None:
        """
        Move the drone in a discrete action space based on the pressed key.

        Parameters:
            - key: The key corresponding to the pressed action.
        """
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
    def angle(self) -> float: 
        """Get the current angle of the drone."""
        return self._angle
    
    @property
    def angular_speed(self) -> float: 
        """Get the angular speed of the drone."""
        return self._angular_speed