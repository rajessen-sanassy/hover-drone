import os
import pygame
from typing import Any, Dict

BASE_PATH = os.path.realpath("hover_drone_gym/assets")
DRONE_IMAGE1 = os.path.join(BASE_PATH, 'drone_1.png')
DRONE_IMAGE2 = os.path.join(BASE_PATH, 'drone_2.png')
BUILDING_IMAGE = os.path.join(BASE_PATH, 'building.png')
BG_IMAGE = os.path.join(BASE_PATH, 'background.png')

def load_images() -> Dict[str, Any]:
    images = {}
    
    try:
        images["drone_1"] = pygame.image.load(DRONE_IMAGE1).convert_alpha()
        images["drone_2"] = pygame.image.load(DRONE_IMAGE2).convert_alpha()
        images["building"] = pygame.image.load(BUILDING_IMAGE).convert_alpha()
        images["background"] = pygame.image.load(BG_IMAGE).convert_alpha()
    except FileNotFoundError as e:
        raise FileNotFoundError("Cannot find the assets folder!\n"
                                f"pointing to directory: {e}") from e
    return images