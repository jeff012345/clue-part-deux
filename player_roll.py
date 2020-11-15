from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional

import pygame
import pygame_gui

from player import HumanPlayer
from paths import Board, board_spaces, doors
from game_board_util import scale_position
from definitions import roll_dice
from log_book_ui import LogBookPanel
from definitions import RoomPosition

class PlayerRoll:
    
    ### Static
    def _is_adjacent(p1, p2):
        return (abs(p1[0] - p2[0]) == 1 and p1[1] == p2[1]) \
            or (abs(p1[1] - p2[1]) == 1 and p1[0] == p2[0])

    def _valid_position(pos):
        return pos[0] >= 0 and pos[0] < 25 and pos[1] >= 0 and pos[1] < 24 \
            and board_spaces[pos[0]][pos[1]] != 0

    player: HumanPlayer
    surface: pygame.Surface
    on_end_turn: Callable
    _rolling: bool
    _distance: int
    _positions: List[Position]
    _rect_to_position: Dict[Tuple, Position]
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
        edge = set(self.player.board_position.connections)
        self._positions = list(self._find_all_positions_search(self._distance, edge, set()))     
        
        self._rects = []
        self._rect_to_position = dict()

        for p in self._positions:
            coords = list(map(scale_position, Board.coords_from_position(p)))
            new_rects = list(map(lambda p: pygame.Rect((p[0] - 5, p[1] - 5), (11, 11)), coords))
            
            self._rects.extend(new_rects)

            for r in new_rects:
                self._rect_to_position[(r.x, r.y)] = p

    def _find_all_positions_search(self, distance: int, edge: Set[Position], 
                                   all_positions: Set[Position]) -> Set[Position]:
        if distance == 1:
            return all_positions.union(edge)

        new_edge: Set[Position] = set()

        for p in edge:
            all_positions.add(p)

            for conn in p.connections:
                if conn not in all_positions and conn not in edge \
                        and not (isinstance(p, RoomPosition) and isinstance(conn, RoomPosition)) \
                        and conn != self.player.board_position:
                    # haven't seen this node before
                    new_edge.add(conn)

        return self._find_all_positions_search(distance - 1, new_edge, all_positions)

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
                    org_rect = self._rects[i]
                    self._click_move(self._rect_to_position[(org_rect.x, org_rect.y)])
                    break
                i += 1

    def _click_move(self, pos: Position):
        self.player.move(pos)
        self._rolling = False
        self.on_end_turn()
