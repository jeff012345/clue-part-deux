from typing import Tuple
import pygame

from player import Player
from definitions import Character
from paths import room_coorindates

player_colors = dict()
player_colors[Character.MRS_WHITE] = (255, 255, 255)
player_colors[Character.MRS_PEACOCK] = (0, 0, 255)
player_colors[Character.MISS_SCARLET] = (255, 0, 0)
player_colors[Character.COLONEL_MUSTARD] = (255, 255, 0)
player_colors[Character.MR_GREEN] = (0, 255, 0)
player_colors[Character.PROFESSOR_PLUM] = (128, 0, 128)

piece_radius = 12

class PlayerPiece:

    player: Player

    def __init__(self, player: Player, surface: pygame.Surface):
        self.player = player
        self.surface = surface

    def draw(self):
        pos = self.player.position
        if self.player.room is not None:
            pos = room_coorindates[self.player.room]
        
        pos = scale_position(pos)
        pygame.draw.circle(self.surface, player_colors[self.player.character], pos, piece_radius)


top_pad = 25
left_pad = 20

board_width = 882 - 55
board_height = 865 - 50

scale_width = board_width / 23.85
scale_height = board_height / 24.9

def scale_position(pos: Tuple[int, int]) -> Tuple[int, int]:
    row = top_pad + int(round((pos[0] + 0.5) * scale_height)) 
    col = left_pad + int(round((pos[1] + 0.5) * scale_width))
    return (col, row)
