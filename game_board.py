from typing import List, Set, Dict, Tuple, Optional
import pygame
from player import Player
from Clue import Director, GameStatus
from threading import Lock
from paths import room_coorindates
from definitions import Character

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

top_pad = 17.5
left_pad = 20
piece_radius = 12

player_colors = dict()
player_colors[Character.MRS_WHITE] = (255, 255, 255)
player_colors[Character.MRS_PEACOCK] = (0, 0, 255)
player_colors[Character.MISS_SCARLET] = (255, 0, 0)
player_colors[Character.COLONEL_MUSTARD] = (255, 255, 0)
player_colors[Character.MR_GREEN] = (0, 255, 0)
player_colors[Character.PROFESSOR_PLUM] = (128, 0, 128)

def scale_position(pos: Tuple[int, int]) -> Tuple[int, int]:
    row = int(round(top_pad + (pos[0] * 28) + piece_radius))
    col = int(round(left_pad + (pos[1] * 29.583333) + piece_radius))
    return (col, row)

class PlayerPiece:

    player: Player

    def __init__(self, player: Player, game_display):
        self.player = player
        self.game_display = game_display

    def draw(self):
        pos = self.player.position
        if self.player.room is not None:
            pos = room_coorindates[self.player.room]
        
        pos = scale_position(pos)
        pygame.draw.circle(self.game_display, player_colors[self.player.character], pos, piece_radius)

def run(director: Director, run_game_lock: Lock, end_game_lock: Lock):
    pygame.init()

    display_width = 750
    display_height = 800

    game_display = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Clue')

    clock = pygame.time.Clock()
    crashed = False

    # load images
    board_img = pygame.image.load('assets/board.jpg')

    player_pieces: List[PlayerPiece] = list(map(lambda p: PlayerPiece(p, game_display), director.players))
    run_game_lock.release()

    while not crashed and end_game_lock.locked() is False:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
                end_game_lock.acquire()

            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_SPACE and run_game_lock.locked() is True:
            #        run_game_lock.release()

            #print(event)
    
        game_display.fill(white)
    
        board_rect = game_display.blit(board_img, (0, 0))

        if director.game_status == GameStatus.RUNNING:
            for player in player_pieces:
                player.draw()

        pygame.display.update()
        clock.tick(60)
                

    pygame.quit()



