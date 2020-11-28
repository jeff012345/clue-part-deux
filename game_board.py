from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional
import pygame
import pygame_gui

from player import *
from definitions import Room
from ai_players import RLPlayer
from Clue import Director, GameStatus
from threading import Lock, Condition, Barrier
from log_book_ui import LogBookPanel
from panels import *
from game_board_util import scale_position, PlayerPiece
from player_roll import PlayerRoll

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

board_width = 882

display_width = LogBookPanel.PANEL_WIDTH + board_width
display_height = 865

def run(director: Director, run_game_lock: Lock, end_game_lock: Lock, human: HumanPlayer, turn_lock: Lock):
    pygame.init()   

    pygame.display.set_caption('Clue')
    game_display = pygame.display.set_mode((display_width, display_height))    

    manager = pygame_gui.UIManager((display_width, display_height), 'theme.json')

    clock = pygame.time.Clock()
    crashed = False   

    # load images
    board_img = pygame.image.load('assets/board.jpg')

    start_button_rect = pygame.Rect(((display_width / 2) - 50, (display_height / 2) - 25), (100, 50))
    start_button = pygame_gui.elements.UIButton(relative_rect=start_button_rect,
                                             text='Start Game',
                                             manager=manager)

    board_surface = pygame.Surface((board_width, display_height))
    
    player_pieces: List[PlayerPiece] = list(map(lambda p: PlayerPiece(p, board_surface), director.players))

    on_end_turn = lambda: end_turn(turn_lock)    

    player_roll = PlayerRoll(board_surface, human, on_end_turn)
    log_book_ui = LogBookPanel(manager)
    guess_panel = GuessPanel(manager, display_width, display_height, human, on_end_turn)
    start_turn_menu = StartTurnPanel(manager, display_width, display_height, player_roll, guess_panel, human)
    match_pick_panel = MatchPickPanel(manager, display_width, display_height, human, on_end_turn)

    human.on_turn = lambda turn: on_player_turn(manager, turn, turn_lock, start_turn_menu, match_pick_panel, on_end_turn)

    started = False
    while end_game_lock.locked() is False and not started:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game(end_game_lock, run_game_lock, turn_lock)
                break
            
            elif event.type == pygame.USEREVENT:
                 if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                     if event.ui_element == start_button:
                         start_button.kill()
                         run_game_lock.release()
                         started = True

            manager.process_events(event)
    
        game_display.fill(white)
                
        manager.update(time_delta)
        manager.draw_ui(game_display)

        pygame.display.update()
    
    if started:
        # start the game
        log_book_ui.show()

        while end_game_lock.locked() is False:
            time_delta = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game(end_game_lock, run_game_lock, turn_lock)
                    break
            
                start_turn_menu.process_events(event)
                log_book_ui.process_events(event)            
                player_roll.process_events(event)
                match_pick_panel.process_events(event)
                guess_panel.process_events(event)
                manager.process_events(event)
    
            game_display.fill(white)
                
            board_surface.blit(board_img, (0, 0))        

            if director.game_status == GameStatus.RUNNING:
                for player in player_pieces:
                    player.draw()

            player_roll.draw()

            game_display.blit(board_surface, (LogBookPanel.PANEL_WIDTH, 0))        

            manager.update(time_delta)
            manager.draw_ui(game_display)

            pygame.display.update()                

    pygame.quit()

def on_player_turn(manager, turn_data: HumanTurn, lock: Lock, start_turn_menu: StartTurnPanel, \
        match_pick_panel: MatchPickPanel, on_end_turn: Callable[[Lock]]):

    print("player turn")
    lock.acquire()
    print("starting player turn")

    if isinstance(turn_data, PickMatchTurn):
        match_pick_panel.show(turn_data)
    elif isinstance(turn_data, GuessOutcome):
        if turn_data.match is None:
            message = "No one showed a card!"
        else:
            player_name = turn_data.showing_player.character.pretty()
            card: Enum = None

            if turn_data.match.character is not None:
                card = turn_data.match.character
            elif turn_data.match.weapon is not None:
                card = turn_data.match.weapon
            else:
                card = turn_data.match.room

            message = player_name + " has showed you " + str(card)

        rect = create_modal_rect(display_width, display_height, 300, 160)
        EndTurnWindow(rect, manager, on_end_turn, "Guess Result", message)
    elif isinstance(turn_data, AccusationOutcome):
        message = None
        if turn_data.correct:
            message = 'You Win! Your accusation is correct!'
        else:
            message = 'You have lost! Your accusation is incorrect.'

        message += '<br><br><strong>Solution:</strong> ' + str(turn_data.solution)

        rect = create_modal_rect(display_width, display_height, 400, 200)
        EndTurnWindow(rect, manager, on_end_turn, "Accusation Result", message)
    elif isinstance(turn_data, OpponentGuess):
        player_name = turn_data.opponent.character.pretty()
        message = "Player " + player_name + " made a guess.<br><br >" + str(turn_data.guess)
        rect = create_modal_rect(display_width, display_height, 400, 200)
        EndTurnWindow(rect, manager, on_end_turn, "Opponent Guess", message)
    elif isinstance(turn_data, DealCard):
        message = "You have been dealt the following cards<br>"
        for card in turn_data.cards:
            message += str(card) + "<br>"
        
        rect = create_modal_rect(display_width, display_height, 400, 200)
        EndTurnWindow(rect, manager, on_end_turn, "Dealt Cards", message)
    elif isinstance(turn_data, GameOver):
        player_name = turn_data.winner.character.pretty()
        message = "You have lost! " + player_name + " is the winner!"
        message += "<br><strong>Solution:</strong> " + str(turn_data.solution)

        if isinstance(turn_data.winner, RLPlayer):
            message += "Winner was the AI"

        rect = create_modal_rect(display_width, display_height, 400, 200)
        EndTurnWindow(rect, manager, on_end_turn, "Game Over", message)
    else:
        start_turn_menu.show()

def end_turn(lock: Lock):
    print("player end turn")
    lock.release()

def quit_game(end_game_lock, run_game_lock, turn_lock):
    end_game_lock.acquire()

    if run_game_lock.locked():
        run_game_lock.release()

    if turn_lock.locked():
        turn_lock.release()    

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
    turn_lock = Lock()
    director = Director(end_game_lock, players, turn_lock)	
    
    run(director, run_game_lock, end_game_lock, human, turn_lock)