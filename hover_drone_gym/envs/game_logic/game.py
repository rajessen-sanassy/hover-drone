import pygame
from hover_drone_gym.envs.game_logic.drone import Drone
from hover_drone_gym.envs.game_logic.building import Building
from math import sqrt, cos, sin, pi, pow
import numpy as np

class Game():
    def __init__(self, screen_size, building_gap, spawn_rate, continuous):
        pygame.init()
        self._screen_width = screen_size[0]
        self._screen_height = screen_size[1]
        self._images = {}

        self._recurr_buildings = spawn_rate
        self._building_gap = building_gap
        self._continuous = continuous

        self._score = 0
        self._building_group = []
        self._radars = [(0,0) * 9]
     
        self._moving = False
        self._gameover = False
        self._prev_building = None                            
        self._drone = None
        # np.random.seed(1)

    def get_raycast(self) -> [float, float, float, float, float, float, float]:
        """Get normalized raycast values from the drone's radars."""
        return np.array([raycast[1] for raycast in self._radars])/780

    def get_velocity(self) -> [float, float]:
        """Get normalized drone velocity."""
        # return sqrt(self.drone.velocity_x**2 + self.drone.velocity_y**2)/10
        return np.array([self.drone.velocity_x, self.drone.velocity_y]) / 4

    def get_angle(self) -> float: 
        """Get normalized drone angle."""
        return self.drone.angle / 180

    def get_angle_velocity(self) -> float: 
        """Get normalized drone angular velocity."""
        return self.drone.angular_speed

    def get_angle_to_target(self) -> float:
        """Get normalized angle to the target building."""
        target = self._get_target()
        if not target: return 0.0

        x, y = self.drone.position
        xt, yt = target[1]
        return np.arctan2(yt - y, xt - x) / pi
    
    def get_distance_to_target(self) -> int:
        """Get distance to the target (between buildings). NOT USED"""
        target = self._get_target()
        if not target: return 0

        point1 = self.drone.position
        point2 = target[1]

        return sqrt(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2))

    def get_x_distance(self) -> int:
        """Get x-distance to the target building."""
        x = 0
        target = self._get_target()
        if not target: return 0
        for buildings in self.building_group:
            if(buildings[0].passed): continue
            x = target[1][0] - self.drone.position_x
            return x
        return x

    def update_state(self, action: int or np.array) -> bool:
        """Update the game state based on the given action."""
        self._moving = True

        self._drone.action(action)

        # Update drone position
        velocity = self._drone.update()

        # Create new buildings
        if not self._prev_building or self._prev_building.position_x < (self._screen_width - self._recurr_buildings):
                self._prev_building = self._create_building()

        for buildings in self._building_group:
            delete = False
            for building in buildings:
            # Update building position
                if(building.update(velocity)):
                    # delete building
                    delete = True
                    del building
            if delete:
                self._building_group.remove(buildings)
        
        # Get score
        self._score += self.evaluate()

        self._radars.clear()
        degrees = [-90, -45, -30, -15, 0, 15, 30, 45, 90]
        for degree in degrees:
            self._check_radar(degree)

        return self._check_collisions()
    
    def evaluate(self) -> int:
        """Evaluate and update the score based on the drone's position."""
        score = 0
        for buildings in self.building_group:
            if buildings[0].evaluate(self.drone.position_x):
                    buildings[1].evaluate(self.drone.position_x)
                    score += 1
        return score

    def action(self, action=None) -> bool:
        """Perform an action in the game."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not self._moving and not self._gameover:
                if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT]:
                    self._moving = True

        if (self._moving and action is None):
            key = pygame.key.get_pressed()

            if key[pygame.K_UP]:
                key = 0
            elif key[pygame.K_DOWN]:
                key = 1
            elif key[pygame.K_LEFT]:
                key = 2
            elif key[pygame.K_RIGHT]:
                key = 3
            else:
                key = 4

            return self.update_state(key)
        else:
            return self.update_state(action)

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self._score = 0
        self._building_group = []
        self._radars = [(0,0) * 9]
     
        self._moving = False
        self._gameover = False
        self._prev_building = None

        if self._drone:
            del self._drone
        
        self._drone = Drone(100, int(self._screen_height/2), self._continuous)

    def _create_building(self) -> [object, object]:
        """Create a new pair of upper and lower buildings."""
        height_upperbound = (self._screen_height/2) - self._building_gap
        height_lowerbound = (-1) * ((self._screen_height/2)-self._building_gap)
        building_height = np.random.randint(height_lowerbound, height_upperbound)

        lower_building = Building(self._screen_width, 
                                  int(self._screen_height/2) + building_height, 
                                  -1, 
                                  self._building_gap)
        upper_building = Building(self._screen_width, 
                                  int(self._screen_height/2) + building_height, 
                                  1, 
                                  self._building_gap)
        
        self.building_group.append((lower_building, upper_building))
        return lower_building

    def _check_radar(self, degree: int) -> None:
        """Check the radar for obstacles."""
        center = self.drone.position
        angle_radian = degree * pi / 180
        length = self._screen_width - self.drone.position_x

        # Calculate the endpoint of the line using y = mx + b
        x_end = int(center[0] + cos(angle_radian) * length)
        y_end = int(center[1] + sin(angle_radian) * length)

        # Cut the line short using intercept functions
        x, y, dist = self._cut_line([(center[0], center[1]), (x_end, y_end)])
        self.radars.append([(x, y), dist])
    
    def _cut_line(self, line1: [(int, int), (int, int)]):
        """Cut the line short based on intercept functions."""
        min_x, min_y = line1[1][0], line1[1][1]
        center_x, center_y = line1[0][0], line1[0][1]
        min_dist = int(sqrt(pow(min_x - center_x, 2) + pow(min_y - center_y, 2)))
        
        for intercept_line in self._get_intercept_lines():
            if self._are_lines_intersecting(line1, intercept_line):
                x, y = self._find_intersection(line1, intercept_line)
                dist = int(sqrt(pow(x - center_x, 2) + pow(y - center_y, 2)))
                if dist <= min_dist:
                    min_x = x
                    min_y = y
                    min_dist = dist

        return min_x, min_y, min_dist
       
    def _get_intercept_lines(self):
        """Get the lines for floor, ceiling, and buildings."""
        floor_line = [(0, self._screen_height), (self._screen_width, self._screen_height)]
        ceiling_line = [(0, 0), (self._screen_width, 0)]
        
        yield floor_line
        yield ceiling_line

        for buildings in self.building_group:
            for building in buildings:
                building_lines = building.get_rect_lines()
                yield from building_lines
    
    def _find_intersection(self, 
                           line1: [(int, int), (int, int)], 
                           line2: [(int, int), (int, int)]):
        """Find the intersection point of two lines."""
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        # Calculate the slopes of the lines
        m1 = (y2 - y1) / ((x2 - x1) + 0.0000001)
        m2 = (y4 - y3) / ((x4 - x3) + 0.0000001)

        # Calculate the y-intercepts
        b1 = y1 - m1 * x1
        b2 = y3 - m2 * x3

        # Calculate the x-coordinate of the intersection point
        x_intersect = (b2 - b1) / (m1 - m2)

        # Calculate the y-coordinate of the intersection point
        y_intersect = m1 * x_intersect + b1

        return int(x_intersect), int(y_intersect)

    def _get_target(self) -> ([tuple], (int, int)):
        """Get the target building."""
        for buildings in self.building_group:
            if(not buildings[0].passed):
                building_top = buildings[1].get_rect_lines()
                building_bottom = buildings[0].get_rect_lines()
                
                return [building_top[1], (building_top[3][1], building_bottom[3][0]),
                    building_bottom[2], (building_bottom[0][1], building_top[0][0])], \
                    (building_bottom[2][1][0], int((building_top[0][0][1] + building_bottom[2][0][1])/2))
        return False

    def _check_collisions(self) -> bool:
        """Check for collisions with obstacles."""
        for intercept_line in self._get_intercept_lines():
            if self._check_hitbox(intercept_line):
                self._gameover = True
                return True
        return False
    
    def _check_hitbox(self, intercept_line):
        """Check for collisions with drone's hitbox."""
        for drone_line in self.drone.get_rect_lines():
            if self._are_lines_intersecting(drone_line, intercept_line):
                return True
            
        return False
    
    def _are_lines_intersecting(self, line1, line2):
        """Check if two lines are intersecting."""
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

    @property
    def drone(self) -> object: 
        """Get the drone object."""
        return self._drone
    
    @property
    def building_group(self) -> [object]: 
        """Get the list of buildings."""
        return self._building_group
    
    @property
    def radars(self) -> [int]:
        """Get the radar data."""
        return self._radars
    
    @property
    def moving(self) -> bool:
        """Get status of game start."""
        return self._moving

    @property
    def score(self) -> int: 
        """Get game score."""
        return self._score