from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional

import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UILabel, UITextBox, UIButton, UIImage, UIDropDownMenu

from player import HumanPlayer, PickMatchTurn
from definitions import *
      
def create_modal_rect(screen_width: int, screen_height: int, width: int, height: int):
    top_offset = round((screen_height / 2) - (height / 2))
    left_offset = round((screen_width / 2) - (width / 2))

    return pygame.Rect((left_offset, top_offset), (width, height))

class StartTurnPanel:

    player: HumanPlayer
    panel: UIPanel
    player_roll: PlayerRoll
    guess_panel: GuessPanel
    
    _roll_button: UIButton
    _guess_button: UIButton
    _accuse_button: UIButton

    def __init__(self, manager: UIManager, screen_width: int, screen_height: int, player_roll: PlayerRoll, \
            guess_panel: GuessPanel, player: HumanPlayer):

         self._create_panel(manager, screen_width, screen_height)
         self.player_roll = player_roll
         self.guess_panel = guess_panel
         self.player = player
   
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
        self._roll_button = UIButton(roll_button_rect, 'Roll', manager, container=self.panel)

        y_offset += 25 + 50

        rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._guess_button = UIButton(rect, 'Guess', manager, container=self.panel)

        y_offset += 25 + 50

        rect = pygame.Rect((50, y_offset + 25), (200, 50))
        self._accuse_button = UIButton(rect, 'Accuse', manager, container=self.panel)

        self.hide()

    def show(self):
        if self.player.room is None:
            self._guess_button.disable()
        else:
            self._guess_button.enable()
        self._guess_button.rebuild()

        self.panel.show()

    def hide(self):
        self.panel.hide()

    def process_events(self, event):
        if not self.panel.visible:
            return

        self.panel.process_event(event)

        if event.type != pygame.USEREVENT:
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            self._button_press(event)

    def _button_press(self, event):
        if event.ui_element == self._roll_button:
            self.hide()
            self.player_roll.roll()

        elif event.ui_element == self._guess_button:
            self.hide()
            self.guess_panel.show_guess()

        elif event.ui_element == self._accuse_button:
            self.hide()
            self.guess_panel.show_accuse()

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

        self._weapon_button.set_text(str(turn_data.guess.weapon))
        self._character_button.set_text(str(turn_data.guess.character))
        self._room_button.set_text(str(turn_data.guess.room))

        self.panel.show()

    def process_events(self, event):
        if not self.panel.visible:
            return

        self.panel.process_event(event)

        if event.type != pygame.USEREVENT:
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

    ###
    ### STATIC
    ###
    def card_from_text(dropdown: UIDropDownMenu, items: Enum, cardType: CardType) -> Card:
        text = dropdown.selected_option

        for item in items:
            if text == item.pretty():
                return Card(item, cardType)

        raise Exception("enum value not found " + text + " " + str(items))

    manager: UIManager
    panel: UIPanel
    player: HumanPlayer
    on_end_turn: Callable

    _weapon_menu: UIDropDownMenu
    _character_menu: UIDropDownMenu
    _room_menu: UIDropDownMenu
    _guess_button: UIButton
    _room_menu_rect: pygame.Rect

    guess: Solution
    is_guess: bool

    def __init__(self, manager: UIManager, screen_width: int, screen_height: int, player: HumanPlayer, \
            on_end_turn: Callable):
        self.manager = manager
        self.player = player
        self.on_end_turn = on_end_turn
        self._create_panel(manager, screen_width, screen_height)
   
    def _create_panel(self, manager: UIManager, screen_width: int, screen_height: int):
        self.width = 300
        self.height = 355

        rect = create_modal_rect(screen_width, screen_height, self.width, self.height)
        self.panel = UIPanel(rect, 0, manager, element_id='guess_panel')

        y_offset = 20

        self.make_label("Make a guess", y_offset)
        y_offset += 20 + 20

        self._character_menu = self.make_drop_down(Character, y_offset)
        y_offset += 25 + 10

        self.make_label("in the", y_offset)
        y_offset += 20 + 10

        self._room_menu = self.make_drop_down(Room, y_offset)
        y_offset += 25 + 10

        self.make_label("with the", y_offset)
        y_offset += 20 + 10

        self._weapon_menu = self.make_drop_down(Weapon, y_offset)
        y_offset += 20 + 50

        button_rect = pygame.Rect((50, y_offset), (200, 30))
        self._guess_button = UIButton(button_rect, '', manager, container=self.panel)

        self.panel.hide()

    def make_label(self, text: str, y_offset):
        rect = pygame.Rect((0, y_offset), (self.width, 20))
        UILabel(rect, text, self.manager, container=self.panel)

    def make_drop_down(self, enum: Enum, y_offset: int) -> UIDropDownMenu:
        items = list(map(lambda i: i.pretty(), enum))
        rect = pygame.Rect((int((self.width - 200) / 2), y_offset), (200, 25))

        if enum == Room:
            self._room_menu_rect = rect

        return UIDropDownMenu(items, items[0], rect, self.manager, container=self.panel)

    def show_guess(self):
        self.is_guess = True
        self._guess_button.set_text('Guess!')

        rect = self._room_menu_rect.copy()
        items = list(map(lambda i: i.pretty(), Room))
        self._room_menu.kill()
        self._room_menu = UIDropDownMenu(items, self.player.room.pretty(), rect, self.manager, container=self.panel)
        #self._room_menu.rebuild()
        self._room_menu.disable()

        self._show()

    def show_accuse(self):
        self.is_guess = False
        self._guess_button.set_text('Make Accusation!')
        self._room_menu.enable()
        self._show()

    def _show(self):
        self.guess = Solution(None, None, None)
        self._update_weapon()
        self._update_character()
        self._update_room() 

        self.panel.show()

    def process_events(self, event):
        if not self.panel.visible:
            return

        self.panel.process_event(event)

        if event.type != pygame.USEREVENT:
            return

        if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self._weapon_menu:
                self._update_weapon()
            elif event.ui_element == self._character_menu:
                self._update_character()
            elif event.ui_element == self._room_menu:
                self._update_room()                

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self._guess_button:
            print("guessing " + str(self.guess))
            self.panel.hide()

            if self.is_guess:
                self.player.make_guess(self.guess)
            else:
                self.player.accuse(self.guess)
            self.on_end_turn()

    def _update_weapon(self):
        self.guess.weapon = GuessPanel.card_from_text(self._weapon_menu, Weapon, CardType.WEAPON)

    def _update_character(self):
        self.guess.character = GuessPanel.card_from_text(self._character_menu, Character, CardType.CHARACTER)

    def _update_room(self):
        self.guess.room = GuessPanel.card_from_text(self._room_menu, Room, CardType.ROOM)


class EndTurnWindow(pygame_gui.windows.UIMessageWindow):

    on_end_turn: Callable

    def __init__(self, rect, manager, on_end_turn: Callable, title: str, message: str):        
        super().__init__(rect, message, manager, window_title=title, object_id='#end_turn_window')
        self.on_end_turn = on_end_turn

    def process_event(self, event: pygame.event.Event):
        if not self.visible:
            return

        super().process_event(event)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED \
                and event.ui_object_id == '#end_turn_window.#dismiss_button':
            self.on_end_turn()
            self.kill()
        
