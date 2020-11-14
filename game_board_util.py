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


top_pad = 17.5
left_pad = 20

def scale_position(pos: Tuple[int, int]) -> Tuple[int, int]:
    row = int(round(top_pad + (pos[0] * 28) + piece_radius))
    col = int(round(left_pad + (pos[1] * 29.583333) + piece_radius))
    return (col, row)
