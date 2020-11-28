from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np

from definitions import *

class CardStat:
    COUNT = 2

    times_guessed: np.float64
    #times_not_shown: int
    max_skipped_players_ratio: np.float64

    def __init__(self):
        self.times_guessed = 0.0
        self.max_skipped_players_ratio = 0.0

class StatTracker:

    VALUE_COUNT = 12 * CardStat.COUNT

    _stats: Dict[Card, CardStat]
    _num_of_players: int

    def __init__(self, num_of_players: int):
        self._num_of_players = num_of_players
        self._init_stats()

    def _init_stats(self):
        self._stats = dict()
        for card in Deck.static_deck:
            if card.type != CardType.ROOM:
                self._stats[card] = CardStat()

    def log_guess(self, solution: Solution, skipped_players: int):
        self._log_card(solution.character, skipped_players)
        self._log_card(solution.weapon, skipped_players)

    def _log_card(self, card: Card, skipped_players: int):
        stats: CardStat = self._stats[card]
        stats.times_guessed += 1

        ratio = skipped_players / (self._num_of_players - 1)
        stats.max_skipped_players_ratio = max(ratio, stats.max_skipped_players_ratio)

    def get_stat(self, card):
        return self._stats[card]

    def stat_array(self):
        stats = np.empty((self._num_of_stats(),), dtype=np.float64)

        i = 0
        for card, stat in self._stats.items():
            stats[i] = stat.times_guessed
            stats[i + 1] = stat.max_skipped_players_ratio

            i += 2

        return stats

    def _num_of_stats(self):
        return StatTracker.VALUE_COUNT

class RoomTracker(StatTracker):

    def __init__(self, num_of_players: int):
        super().__init__(num_of_players)

    #override
    def _init_stats(self):
        self._stats = dict()
        for card in Deck.static_deck:
            if card.type == CardType.ROOM:
                self._stats[card] = CardStat()

    # override
    def log_guess(self, solution: Solution, skipped_players: int):
        self._log_card(solution.room, skipped_players)

    # override
    def _num_of_stats(self):
        return 9 * CardStat.COUNT
