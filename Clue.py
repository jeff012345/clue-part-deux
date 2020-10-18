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

PLAYER_ORDER = [
	(Character.MISS_SCARLET, (1, 17)),
	(Character.COLONEL_MUSTARD, (8, 24)),
	(Character.MRS_WHITE, (25, 15)),
	(Character.MR_GREEN, (25, 10)),
	(Character.MRS_PEACOCK, (19, 1)),			
	(Character.PROFESSOR_PLUM, (6, 1))
]

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
	remaining_players: List[Player]
	player_by_character: Dict[Character, Player]
	solution: Solution
	winner: Player
	game_status: GameStatus
	end_game_lock: Lock

	def __init__(self, end_game_lock: Lock, players: List[Player]):
		self.player_by_character = dict()

		self.end_game_lock = end_game_lock
		self.players = players

		for p in self.players:
			p.director = self

	def new_game(self):
		self.winner = None
		self.game_status = GameStatus.READY

		self._assign_players()	
		self._setup_cards()

		self.game_status = GameStatus.INITIALIZED

	def _setup_cards(self):
		deck = Deck.make_deck()
		random.shuffle(deck)

		self.solution = Solution(
			Director._pick_first(deck, CardType.WEAPON),
			Director._pick_first(deck, CardType.CHARACTER),
			Director._pick_first(deck, CardType.ROOM)		
		)

		self._deal_cards(deck)

	def play_auto_game(self):
		if self.game_status != GameStatus.INITIALIZED:
			raise Exception("Game not setup")

		self.game_status = GameStatus.RUNNING

		while not self._end_game():
			for player in self.remaining_players:
				player.take_turn()

				if self._end_game():
					return

		self.game_status = GameStatus.ENDED

	def take_turns_until_player(self, stop_player: Player):
		for player in self.remaining_players:
			if player == stop_player:
				return

			player.take_turn()

			if self._end_game():
				self.game_status = GameStatus.ENDED
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
		for p in self.players:
			p.reset()

		random.shuffle(self.players)
		self.remaining_players = self.players.copy()
				
		self.player_by_character.clear()

		i = 0
		for player in self.players:
			player.character = PLAYER_ORDER[i][0]

			self.player_by_character[player.character] = player

			# assign start location
			start = PLAYER_ORDER[i][1]
			player.position = (start[0] - 1, start[1] - 1)

			i += 1		

	## store the order somewhere so it doesn't need to be calculated each time
	def make_guess(self, player: Player, solution: Solution) -> Solution:
		if not solution.is_complete():
			print('Incomplete guess')
			print(solution)
			print(player.log_book.log_book)
			raise Exception()

		## move the accused player
		try:
			self.player_by_character[solution.character.value].enter_room(solution.room.value)
		except KeyError as err:
			print(self.player_by_character)
			raise err

		## ask each player in order
		skipped_players = 0
		for other_player in self._asking_order(player):
			match = other_player.show_card(solution)

			if match is not None:
				return (match, skipped_players)

			skipped_players += 1

		return (None, skipped_players)

	def _asking_order(self, player: Player) -> List[Player]:
		player_index = self.players.index(player)

		## determine the order to ask each player (clockwise around the board)
		if player_index == 0:
			# first player
			return self.players[1:]
		elif player_index == len(self.players) - 1:
			# last player
			return self.players[:-1]
		else:
			return self.players[player_index+1:] + self.players[0:player_index]

	def make_accusation(self, player: Player, solution: Solution):
		#print(str(player.character) + " is making an accusation")
		#print(solution)

		if self.solution.is_match(solution):
			self.winner = player
			self.game_status = GameStatus.ENDED
		else:
			## player loses and doesn't get any more turns
			self.remaining_players.remove(player)
			print('this shouldn\'t happen')
			raise Exception()
	
	def _end_game(self):
		## no winner and at least 2 players
		return self.winner is not None or len(self.players) == 1 or self.end_game_lock.locked() is True

def new_game(director: Director):
	director.new_game();
	#print("Solution")
	#print(director.solution)


def main():
	sum = 0
	cnt = 0

	players = [
		ComputerPlayer(),
		ComputerPlayer(),
		ComputerPlayer(),
		ComputerPlayer(),
		ComputerPlayer(),
		ComputerPlayer()
	]

	end_game_lock = Lock()
	director = Director(end_game_lock, players)	

	while cnt <= 100:
		start = time.perf_counter()
		director.new_game()
		director.play_auto_game();
		end = time.perf_counter()

		sum += end - start
		cnt += 1

		if cnt % 100 == 0:
			print("Average Time per game = " + str(sum / cnt) +"; Total Games = " + str(cnt))

if __name__ == "__main__":
	main()