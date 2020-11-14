from typing import List, Set, Dict, Tuple, Optional
import pygame
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UILabel, UITextBox, UIButton, UIImage

from definitions import *

class LogBookPanel:

    CHECKED_IMG = pygame.image.load('assets/checked.png')
    UNCHECKED_IMG = pygame.image.load('assets/unchecked.png')
    PANEL_WIDTH = 200

    panel: UIPanel
    _checkboxes: Dict[UIImage, bool]

    def __init__(self, manager: UIManager):
        self.manager = manager 

        self._checkboxes = dict()

        panel_rect = pygame.Rect((0,0), (LogBookPanel.PANEL_WIDTH, 1000))

        self.panel = UIPanel(panel_rect, 0, manager, element_id='log_book_panel')

        UILabel(pygame.Rect((0,0), (LogBookPanel.PANEL_WIDTH, 20)), 
                "Player Logbook", 
                manager, 
                container=self.panel,
                object_id="categoryLabel")

        height = self._create_section("Chacater", Character, 20)
        height = self._create_section("Room", Room, height)
        self._create_section("Weapon", Weapon, height)      

    def process_events(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
        
            # check if click is inside panel first?

            for cb in self._checkboxes.keys():
                if cb.get_abs_rect().collidepoint(pos):
                    self._toggle_img(cb)
                    break

    def _create_section(self, title: str, items: Enum, y_offset) -> int:
        item_height = 35

        label_rect = pygame.Rect((0, y_offset), (LogBookPanel.PANEL_WIDTH, item_height))
        label_text = "<strong>" + title + "</strong>"
        title_label = UITextBox(label_text, label_rect, self.manager, container=self.panel)
    
        y_offset += item_height

        item_label_width = LogBookPanel.PANEL_WIDTH - 30

        for item in items:
            img_rect = pygame.Rect((5, y_offset + 6), (24, 24))
            checkbox_img = UIImage(img_rect, LogBookPanel.UNCHECKED_IMG, self.manager, container=self.panel)

            label_rect = pygame.Rect((30, y_offset), (item_label_width, item_height))
            item_button = UITextBox(item.name, label_rect, self.manager, container=self.panel)

            self._checkboxes[checkbox_img] = False

            y_offset += item_height

        return y_offset

    def _toggle_img(self, checkbox: UIImage):
        if self._checkboxes.get(checkbox):
            checkbox.set_image(LogBookPanel.UNCHECKED_IMG)
            self._checkboxes[checkbox] = False
        else:
            checkbox.set_image(LogBookPanel.CHECKED_IMG)
            self._checkboxes[checkbox] = True