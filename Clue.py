from enum import Enum
from typing import List, Set, Dict, Tuple, Optional
import random
from paths import RoomPath, Board
from definitions import *
from player import *
from threading import Lock
import time

class GameStatus(Enum):
	INITIALIZED = 1
	READY = 2
	RUNNING = 3
	ENDED = 4

class Director:
	
	## static
	def _pick_first(deck: List[Card], type: CardType) -> Card:
		i = 0
		for card in deck:
			if card.type == type:
				return deck.pop(i)
			i += 1
		
		return None

	players: List[Player]
	player_by_character: Dict[Character, Player]
	solution: Solution
	winner: Player
	game_status: GameStatus
	end_game_lock: Lock

	def __init__(self, end_game_lock: Lock):
		self.end_game_lock = end_game_lock
		self.players = []
		self.game_status = GameStatus.INITIALIZED

	def _reset(self):
		self.winner = None
		self.game_status = GameStatus.READY

	def new_game(self):
		self._reset()
		self._assign_players()
		self._setup()
		
		self._play_game()

		if self.winner is not None:
			print("Winner is " + str(self.winner))
		else:
			## no more opponents left
			print(str(self.players[0]) + " wins by default")

		self.game_status = GameStatus.ENDED

	def register_player(self, player: Player):
		self.players.append(player)

	def _setup(self):
		deck = Deck.make_deck()
		random.shuffle(deck)

		self.solution = Solution(
			Director._pick_first(deck, CardType.WEAPON),
			Director._pick_first(deck, CardType.CHARACTER),
			Director._pick_first(deck, CardType.ROOM)		
		)

		self._deal_cards(deck)

	def _play_game(self):		
		self.game_status = GameStatus.RUNNING

		while not self._end_game():
			for player in self.players:
				player.take_turn()

				#time.sleep(1)

				if self._end_game():
					return

	def _deal_cards(self, deck):
		i = 0
		num_of_players = len(self.players)

		for card in deck:
			self.players[i].give_card(card)
			i += 1

			if i == num_of_players:
				i = 0

	def _assign_players(self):
		random.shuffle(self.players)

		order = [
			(Character.MISS_SCARLET, (1, 17)),
			(Character.COLONEL_MUSTARD, (8, 24)),
			(Character.MRS_WHITE, (25, 15)),
			(Character.MR_GREEN, (25, 10)),
			(Character.MRS_PEACOCK, (19, 1)),			
			(Character.PROFESSOR_PLUM, (6, 1))
		]

		self.player_by_character = dict()

		i = 0
		for player in self.players:
			player.character = order[i][0]
			self.player_by_character[player.character] = player

			#assign start location
			start = order[i][1]
			player.position = (start[0] - 1, start[1] - 1)

			i += 1		

	## store the order somewhere so it doesn't need to be calculated each time
	def make_guess(self, player: Player, solution: Solution) -> Solution:
		## move the accused player
		self.player_by_character[solution.character.value].enter_room(solution.room.value)

		player_index = self.players.index(player)

		## determine the order to ask each player (clockwise around the board)
		if player_index == 0:
			# first player
			other_players = self.players[1:]
		elif player_index == len(self.players) - 1:
			# last player
			other_players = self.players[:-1]
		else:
			other_players = self.players[player_index+1:] + self.players[0:player_index]

		## ask each player in order
		for other_player in other_players:
			match = other_player.show_card(solution)

			if match is not None:
				return match

		return None

	def make_accusation(self, player: Player, solution: Solution):
		print(str(player.character) + " is making an accusation")
		print(solution)

		if self.solution.is_match(solution):
			self.winner = player
		else:
			## player loses and doesn't get any more turns
			self.players.remove(player)
	
	def _end_game(self):
		## no winner and at least 2 players
		return self.winner is not None or len(self.players) == 1 or self.end_game_lock.locked() is True

def new_game(director: Director):
	director.new_game();
	print("Solution")
	print(director.solution)