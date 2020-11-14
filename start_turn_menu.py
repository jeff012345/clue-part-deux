from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional

import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UILabel, UITextBox, UIButton, UIImage

from player import HumanPlayer, PickMatchTurn
import paths
from game_board_util import scale_position
from definitions import roll_dice, Card, Solution
from log_book_ui import LogBookPanel

class PlayerRoll:
    
    ### Static
    def _is_adjacent(p1, p2):
        return (abs(p1[0] - p2[0]) == 1 and p1[1] == p2[1]) \
            or (abs(p1[1] - p2[1]) == 1 and p1[0] == p2[0])

    def _valid_position(pos):
        return pos[0] >= 0 and pos[0] < 25 and pos[1] >= 0 and pos[1] < 24 \
            and paths.board_spaces[pos[0]][pos[1]] != 0

    player: HumanPlayer
    surface: pygame.Surface
    on_end_turn: Callable
    _rolling: bool
    _distance: int
    _positions: List[Tuple[int, int]]
    _rects: List[pygame.Rect]
    _drawn_rects: List[pygame.Rect]

    def __init__(self, surface: pygame.Surface, player: HumanPlayer, on_end_turn: Callable):
        self.surface = surface
        self._rolling = False
        self.player = player
        self.on_end_turn = on_end_turn

    def roll(self):
        self._rolling = True
        self._distance = roll_dice()
        print("rolled a " + str(self._distance))

        self._calculate_positions()

    def _calculate_positions(self):
        start = self.player.position

        self._positions = []

        # from left to right, scale up to down for space that fix within 
        # the roll and are valid positions
        x_offset = -1 * self._distance
        while x_offset <= self._distance:
            y_offset = 0

            while abs(y_offset) + abs(x_offset) <= self._distance:
                # up
                pos = (start[0] + x_offset, start[1] + y_offset)
                if PlayerRoll._valid_position(pos):
                    self._positions.append(pos)

                # down
                pos = (start[0] + x_offset, start[1] + y_offset * -1)
                if PlayerRoll._valid_position(pos):                 
                    self._positions.append(pos)

                y_offset += 1

            x_offset += 1

        self._remove_invalid_positions()

        self._rects = list(map(scale_position, self._positions))
        self._rects = list(map(lambda p: pygame.Rect((p[0] - 5, p[1] - 5), (11, 11)), self._rects))

    # remove positions that don't actually correct to the rest of them
    def _remove_invalid_positions(self):
        no_dupe_positions = []

        # remove duplicates
        for position in self._positions:
            dupe = False
            for cmp in no_dupe_positions:
                if position[0] == cmp[0] and position[1] == cmp[1]:
                    dupe = True
                    break

            if not dupe:
                no_dupe_positions.append(position)

        good_positions = []
        for position in no_dupe_positions:
            for cmp in no_dupe_positions:
                if position[0] == cmp[0] and position[1] == cmp[1]:
                    continue

                if PlayerRoll._is_adjacent(position, cmp):
                    good_positions.append(position)
                    break               

        self._positions = good_positions

    def draw(self):
        if not self._rolling:
            return      
        
        self._drawn_rects = list(map(lambda rect: pygame.draw.rect(self.surface, (120, 120, 120), rect), self._rects)) 

    def process_events(self, event):
        if not self._rolling:
            return

        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            i = 0
            for rect in self._drawn_rects:
                rect = rect.move(LogBookPanel.PANEL_WIDTH, 0)

                if rect.collidepoint(pos):
                    self._click_move(self._positions[i])
                    break
                i += 1

    def _click_move(self, pos):
        self.player.position = pos
        self._rolling = False
        self.on_end_turn()
      
def create_modal_rect(screen_width: int, screen_height: int, width: int, height: int):
    top_offset = round((screen_height / 2) - (height / 2))
    left_offset = round((screen_width / 2) - (width / 2))

    return pygame.Rect((top_offset, left_offset), (width, height))

class StartTurnPanel:

    panel: UIPanel
    player_roll: PlayerRoll

    def __init__(self, display, manager: UIManager, screen_width: int, screen_height: int, player_roll: PlayerRoll):
         self._create_panel(manager, screen_width, screen_height)
         self.player_roll = player_roll
   
    def _create_panel(self, manager: UIManager, screen_width: int, screen_height: int):
        self.width = 300
        self.height = 275

        rect = create_modal_rect(screen_width, screen_height, self.width, self.height)
        self.panel = UIPanel(rect, 0, manager, element_id='start_turn')

        UILabel(pygame.Rect((0, 10), (self.width, 20)), 
                "Your Turn", 
                manager, 
                container=self.panel,
                object_id="windowTitle")

        y_offset = 10 + 10

        roll_button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self.roll_button = UIButton(roll_button_rect, 'Roll', manager, container=self.panel)

        y_offset += 25 + 50

        guess_button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        guess_button = UIButton(guess_button_rect, 'Guess', manager, container=self.panel)

        y_offset += 25 + 50

        accuse_button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self.accuse_button = UIButton(accuse_button_rect, 'Accuse', manager, container=self.panel)

        self.hide()   

    def show(self):
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def process_events(self, event):
        if not self.panel.visible or event.type != pygame.USEREVENT:
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            self._button_press(event)

    def _button_press(self, event):
        if event.ui_element == self.roll_button:
            self.hide()
            self.player_roll.roll()           

class MatchPickPanel:

    panel: UIPanel
    player: HumanPlayer
    pick: Card
    on_end_turn: Callable
    
    _weapon_button: UIButton
    _character_button: UIButton
    _room_button: UIButton
    _solution: Solution

    def __init__(self, manager: UIManager, screen_width: int, screen_height: int, player: HumanPlayer, \
            on_end_turn: Callable):
        self.player = player
        self.on_end_turn = on_end_turn
        self._create_panel(manager, screen_width, screen_height)
   
    def _create_panel(self, manager: UIManager, screen_width: int, screen_height: int):
        self.width = 300
        self.height = 275

        rect = create_modal_rect(screen_width, screen_height, self.width, self.height)
        self.panel = UIPanel(rect, 0, manager, element_id='match_pick_panel')

        UILabel(pygame.Rect((0, 10), (self.width, 20)), 
                "Pick a card to show", 
                manager, 
                container=self.panel)

        y_offset = 10 + 10

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._weapon_button = UIButton(button_rect, '', manager, container=self.panel)

        y_offset += 25 + 50

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._character_button = UIButton(button_rect, '', manager, container=self.panel)

        y_offset += 25 + 50

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._room_button = UIButton(button_rect, '', manager, container=self.panel)

        self.panel.hide()

    def show(self, turn_data: PickMatchTurn):
        solution = turn_data.match
        self._solution = solution

        if solution.weapon is None:            
            self._weapon_button.disable()
        else:
            self._weapon_button.enable()            

        if solution.character is None:            
            self._character_button.disable()
        else:
            self._character_button.enable()

        if solution.room is None:            
            self._room_button.disable()
        else:
            self._room_button.enable()

        self._weapon_button.set_text(str(turn_data.guess.weapon.value.name))
        self._character_button.set_text(str(turn_data.guess.character.value.name))
        self._room_button.set_text(str(turn_data.guess.room.value.name))

        self.panel.show()

    def process_events(self, event):
        if not self.panel.visible or event.type != pygame.USEREVENT:
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            done = False

            if event.ui_element == self._weapon_button:
                self.player.set_card_to_show(self._solution.weapon)
                done = True
            elif event.ui_element == self._character_button:
                self.player.set_card_to_show(self._solution.character)
                done = True
            elif event.ui_element == self._room_button:
                self.player.set_card_to_show(self._solution.room)
                done = True

            if done:
                self.panel.hide()
                self.on_end_turn()

class GuessPanel:

    def __init__(self, manager: UIManager, screen_width: int, screen_height: int, player: HumanPlayer, \
            on_end_turn: Callable):
        self.player = player
        self.on_end_turn = on_end_turn
        self._create_panel(manager, screen_width, screen_height)
   
    def _create_panel(self, manager: UIManager, screen_width: int, screen_height: int):
        self.width = 300
        self.height = 275

        rect = create_modal_rect(screen_width, screen_height, self.width, self.height)
        self.panel = UIPanel(rect, 0, manager, element_id='guess_panel')

        UILabel(pygame.Rect((0, 10), (self.width, 20)), 
                "Make a guess", 
                manager, 
                container=self.panel)

        y_offset = 10 + 10

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._weapon_button = UIButton(button_rect, '', manager, container=self.panel)

        y_offset += 25 + 50

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._character_button = UIButton(button_rect, '', manager, container=self.panel)

        y_offset += 25 + 50

        button_rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._room_button = UIButton(button_rect, '', manager, container=self.panel)

        self.panel.hide()