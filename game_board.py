from typing import List, Set, Dict, Tuple, Optional
import pygame
import pygame_gui

from player import Player, HumanPlayer, NaiveComputerPlayer
from Clue import Director, GameStatus
from threading import Lock
from log_book_ui import LogBookPanel
from start_turn_menu import StartTurnPanel, PlayerRoll
from game_board_util import scale_position, PlayerPiece

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

log_book_width = LogBookPanel.PANEL_WIDTH
board_width = 800

display_width = log_book_width + board_width
display_height = 1000

def run(director: Director, run_game_lock: Lock, end_game_lock: Lock, player: HumanPlayer):
    pygame.init()   

    pygame.display.set_caption('Clue')
    game_display = pygame.display.set_mode((display_width, display_height))    

    manager = pygame_gui.UIManager((display_width, display_height), 'theme.json')

    clock = pygame.time.Clock()
    crashed = False   

    # load images
    board_img = pygame.image.load('assets/board.jpg')

    start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                             text='Start Game',
                                             manager=manager)

    board_surface = pygame.Surface((board_width, 800))
    
    player_pieces: List[PlayerPiece] = list(map(lambda p: PlayerPiece(p, board_surface), director.players))

    player_roll = PlayerRoll(board_surface)
    log_book_ui = LogBookPanel(manager)
    start_turn_menu = StartTurnPanel(game_display, manager, display_width, display_height, player_roll)

    while not crashed and end_game_lock.locked() is False:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
                end_game_lock.acquire()

                if run_game_lock.locked():
                    run_game_lock.release()    
            
            elif event.type == pygame.USEREVENT:
                 if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                     if event.ui_element == start_button:
                         start_button.hide()
                         start_turn_menu.show()
                         #run_game_lock.release()
            
            start_turn_menu.process_events(event)
            log_book_ui.process_events(event)
            manager.process_events(event)
            player_roll.process_events(event)
    
        game_display.fill(white)
                
        board_surface.blit(board_img, (0, 0))  
        player_roll.draw()

        if director.game_status == GameStatus.RUNNING:
            for player in player_pieces:
                player.draw()

        game_display.blit(board_surface, (log_book_width, 0))        

        manager.update(time_delta)
        manager.draw_ui(game_display)     

        pygame.display.update()
                

    pygame.quit()



if __name__ == "__main__":
    human = NaiveComputerPlayer()# HumanPlayer()

    players = [
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		NaiveComputerPlayer(),
		human
	]

    run_game_lock = Lock()
    end_game_lock = Lock()
    director = Director(end_game_lock, players)	
    
    run(director, run_game_lock, end_game_lock, human)