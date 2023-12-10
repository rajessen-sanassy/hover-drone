import pygame

BUILDING_WIDTH = 80
BUILDING_HEIGHT = 560

class Building():
    def __init__(self, x, y, position, building_gap):
        """
        Initialize a Building object.

        Parameters:
            - x: Initial x-coordinate of the building.
            - y: Initial y-coordinate of the building.
            - position: Position identifier (1 or -1).
            - building_gap: Gap between buildings.
        """
        self._rect = pygame.Rect(x, y, BUILDING_WIDTH, BUILDING_HEIGHT)
        self._passed = False
        self._position = position
        self._building_gap = building_gap

        # Adjust the building position based on the specified position
        if position == 1: 
            self._rect.bottomleft = [x, y - self._building_gap]
        elif position == -1:
            self._rect.topleft = [x, y + self._building_gap]
    
    def get_rect_lines(self) -> [tuple]:
        """
        Get the lines representing the building's rectangle.

        Returns:
            - List of line coordinates as tuples.
        """
        x, y = self._rect.x, self._rect.y
        w, h = self._rect.width, self._rect.height

        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)
        return [(bottom_left, top_left), (bottom_right, bottom_left),
                (top_left, top_right), (top_right, bottom_right)]
    
    def evaluate(self, x : int) -> bool:
        """
        Evaluate if the building has been passed by the agent.

        Parameters:
            - x: Current x-coordinate of the agent.

        Returns:
            - Bool, True if passed, False otherwise.
        """
        if(x > self._rect.right and not self._passed):
            self._passed = True
            return True
        return False
    
    def update(self, velocity_x : float) -> bool:
        """
        Update the building's position based on the agent's velocity.

        Parameters:
            - velocity_x: Velocity of the agent along the x-axis.

        Returns:
            - Bool, True if building is off-screen, False otherwise.
        """
        building_speed = max(velocity_x, 0)
        self._rect.x -= building_speed
        
        if self._rect.right < 0:
            return True
        return False

    @property
    def position(self) -> int: 
        """
        Get the position identifier of the building.

        Returns:
            - Position identifier (1 or -1).
        """
        return self._position
    
    @property
    def position_x(self) -> int: 
        """
        Get the x-coordinate of the building.

        Returns:
            - x-coordinate.
        """
        return self._rect.x
    
    @property
    def position_y(self) -> int: 
        """
        Get the y-coordinate of the building.

        Returns:
            - y-coordinate.
        """
        return self._rect.y
    
    
    @property
    def passed(self) -> bool: 
        """
        Check if the building has been passed by the agent.

        Returns:
            - Bool, True if passed, False otherwise.
        """
        return self._passed