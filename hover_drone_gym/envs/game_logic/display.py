
import pygame
from hover_drone_gym.envs.game_logic.utils import load_images
import numpy as np

FILL_BACKGROUND_COLOR = (200, 200, 200)

class Display():
    def __init__(self, 
                 screen_size: tuple, 
                 FPS: int, 
                 visualize=False):
        """
        Initialize the Display object.

        Parameters:
            - screen_size: Tuple representing the screen dimensions (width, height).
            - FPS: Frames per second.
            - visualize: Boolean indicating whether to visualize observation space.
        """
        self._screen_width = screen_size[0]
        self._screen_height = screen_size[1]
        self._clock = pygame.time.Clock()
        self._game_speed = FPS
        self._step = 0
        self._visualize = visualize
        self._scoreFont = None
        self._font = None
        self._images = {}
        self._surface = pygame.Surface(screen_size)
        self._display = None
        self._game = None

    def make_display(self) -> None:
        """
        Create the game display and set up necessary elements.
        """
        self._scoreFont = pygame.font.Font('hover_drone_gym/assets/custom_font.ttf', 30)
        pygame.display.set_caption('Hover Drone')
        self._display = pygame.display.set_mode((self._screen_width, 
                        self._screen_height))
        self._images = load_images()

    def draw_surface(self, reward) -> None:
        """
        Draw the game elements on the display surface.

        Parameters:
            - reward: Current reward value.
        """
        if self._game is None:
            raise ValueError("A game logic must be assigned to the display!")
        
        # Fill background
        if self._images['background'] is not None:
            self._surface.blit(self._images['background'], (0, 0))
        else:
            self._surface.fill(FILL_BACKGROUND_COLOR)

        # Draw buildings, score, drone, and additional elements if visualizing
        self._draw_buildings()
        self._draw_score()
        self._draw_drone()

        if self._visualize and self._game.moving:
            self._draw_hitbox()
            self._draw_raycast()
            self._draw_target()
            self._write_metrics()
            if(reward):
                self._draw_reward(reward)

    def _draw_buildings(self) -> None:
        """
        Draw buildings on the display surface.
        """
        for buildings in self._game.building_group:
            for building in buildings:
                image = self._images['building']
                if building.position==1:
                    image = pygame.transform.flip(image, False, True)
                self._surface.blit(image, # draw building
                                 (building.position_x, building.position_y))

    def _draw_score(self) -> None:
        """
        Draw the score on the display surface.
        """
        text = self._scoreFont.render(f"Score: {self._game.score}", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self._screen_width/2, 20)
        self._surface.blit(text, text_rect)

    def _draw_drone(self) -> None:
        """
        Draw the drone on the display surface.
        """
        self._step += 1
        if(int(self._step * 0.3) % 2):
            player_sprite = self._images["drone_1"]
        else:
            player_sprite = self._images["drone_2"]

        player_copy = pygame.transform.rotate(player_sprite, self._game.drone.angle)
        rotated_rect = player_copy.get_rect(center=self._game.drone._rect.center)
        draw_pos = rotated_rect.topleft
        self._surface.blit(player_copy, draw_pos)

    def _draw_raycast(self) -> None:
        """
        Draw the radar rays on the display surface.
        """
        for radar in self._game.radars:
            position = radar[0]
            pygame.draw.line(self._surface, (0, 255, 0), self._game.drone.position, position, 1)
            pygame.draw.circle(self._surface, (0, 255, 0), position, 5)
    
    def _draw_target(self) -> None:
        """
        Draw the target line and point on the display surface.
        """
        if not self._game.building_group: return
    
        target = self._game._get_target()
        point = (target[1][0], self._game.drone.position_y)
        
        for line in target[0]:
            pygame.draw.line(self._surface, (0, 0, 255), line[0], line[1], 1)
        
        pygame.draw.line(self._surface, (0, 0, 255), self._game.drone.position, point, 1)
        pygame.draw.circle(self._surface, (0, 0, 255), point, 5)

    def _draw_hitbox(self) -> None:
        """
        Draw the drone's hitbox on the display surface.
        """
        for line in self._game.drone.get_rect_lines():
            pygame.draw.line(self._surface, (255, 0, 0), line[0], line[1])

    def _write_metrics(self) -> None:
        """
        Write additional metrics on the display surface.
        """
        font = pygame.font.Font(None, 18)
        text = f"""
            velocity: {self._game.get_velocity()}\n\
            angle: {self._game.get_angle()}\n\
            angle_velocity: {self._game.get_angle_velocity()}
            x_distance to target: {self._game.get_x_distance()}
            raycast: {np.round(self._game.get_raycast(), decimals=5)}\n"""
        
        # distance_to_target: {self._game.get_distance_to_target()}\n\
        # angle_to_target: {self._game.get_angle_to_target()}\n\

        lines = text.splitlines()
        for i, l in enumerate(lines):
            self._surface.blit(font.render(l, True, (0,0,0)), [-20, 0 + 12*i])

    def _draw_reward(self, reward) -> None:
        """
        Draw the reward on the display surface.

        Parameters:
            - reward: Current reward value.
        """
        font = pygame.font.Font(None, 18)
        text = f"reward: {reward}"

        self._surface.blit(font.render(text, True, (0,0,0)), [16, 80])

    def update_display(self) -> None:
        """
        Update the game display.

        Raises:
            - RuntimeError: If a display hasn't been created yet.
        """
        if self._display is None:
            raise RuntimeError(
                "Tried to update the display, but a display hasn't been "
                "created yet! To create a display for the renderer, you must "
                "call the `make_display()` method."
            )
           
        self._display.blit(self._surface, [0, 0])
        pygame.display.update()
        self._clock.tick(self._game_speed)
    
    @property
    def game(self) -> object: 
        """
        Get the associated game logic.

        Returns:
            The game logic instance.
        """
        return self._game
    
    @game.setter 
    def game(self, g):
        """
        Set the associated game logic.

        Parameters:
            - g: Game logic instance.
        """
        self._game = g