from enum import Enum
from typing import List, Set, Dict, Tuple, Optional
import random
from paths import RoomPath
from definitions import *

class Card:

	value: Enum
	type: CardType

	def __init__(self, value: Enum, type: CardType):
		self.value = value
		self.type = type

	def __str__(self):
		return self.value.name

	def __repr__(self):
		return self.value.name

	def __eq__(self, other):
		"""Overrides the default implementation"""
		if isinstance(other, Card):
			return self.type == other.type and self.value == other.value
		return False

	def __ne__(self, other):
		"""Overrides the default implementation (unnecessary in Python 3)"""
		x = self.__eq__(other)
		if x is not NotImplemented:
			return not x
		return NotImplemented

	def __hash__(self):
		"""Overrides the default implementation"""
		return hash(tuple(sorted(self.__dict__.items())))

class Deck:

	def make_deck() -> List[Card]:
		return [
			Card(Room.STUDY, CardType.ROOM),
			Card(Room.LIBRARY, CardType.ROOM),
			Card(Room.CONSERVATORY, CardType.ROOM),
			Card(Room.HALL, CardType.ROOM),
			Card(Room.KITCHEN, CardType.ROOM),
			Card(Room.BALLROOM, CardType.ROOM),			
			Card(Room.DINING_ROOM, CardType.ROOM),
			Card(Room.LOUNGE, CardType.ROOM),
			Card(Room.BILLARD_ROOM, CardType.ROOM),			
			Card(Character.MRS_WHITE, CardType.CHARACTER),
			Card(Character.MRS_PEACOCK, CardType.CHARACTER),
			Card(Character.MISS_SCARLET, CardType.CHARACTER),
			Card(Character.COLONEL_MUSTARD, CardType.CHARACTER),
			Card(Character.MR_GREEN, CardType.CHARACTER),
			Card(Character.PROFESSOR_PLUM, CardType.CHARACTER),
			Card(Weapon.CANDLESTICK, CardType.WEAPON),
			Card(Weapon.REVOLVER, CardType.WEAPON),
			Card(Weapon.ROPE, CardType.WEAPON),
			Card(Weapon.WRENCH, CardType.WEAPON),
			Card(Weapon.LEAD_PIPE, CardType.WEAPON),
			Card(Weapon.KNIFE, CardType.WEAPON),
		]

class Solution:

	weapon: Card
	character: Card
	room: Card

	def __init__(self, weapon: Card, character: Card, room: Card):
		self.weapon = weapon
		self.character = character
		self.room = room

	def is_complete(self):
		return self.weapon is not None and self.room is not None and self.character is not None

	def is_empty(self):
		return self.weapon is None and self.room is None and self.character is None

	def __repr__(self):
		return self.character.value.name + " in the " + self.room.value.name + " with the " + self.weapon.value.name


class Hand:

	all: List[Card]
	weapons: List[Card]
	rooms: List[Card]
	characters: List[Card]

	def __init__(self):
		self.all = []
		self.weapons = []
		self.rooms = []
		self.characters = []

	def add(self, card: Card):
		self.all.append(card)

		if card.type == CardType.WEAPON:
			self.weapons.append(card)
		elif card.type == CardType.ROOM:
			self.rooms.append(card)
		elif card.type == CardType.CHARACTER:
			self.characters.append(card)

	def __repr__(self):
		return str(self.all)


class SolutionMatcher:

	def compare_to_hand(hand: Hand, solution: Solution) -> Solution:
		matches = Solution(None, None, None)

		try:
			hand.weapons.index(solution.weapon)
			matches.weapon = solution.weapon
		except ValueError:
			pass

		try:
			hand.rooms.index(solution.room)
			matches.room = solution.room
		except ValueError:
			pass

		try:
			hand.characters.index(solution.character)
			matches.character = solution.character
		except ValueError:
			pass

		return matches

	def is_match(a: Solution, b: Solution):
		return a.weapon == b.weapon and a.room == b.room and a.character == b.character

class LogBook:

	log_book: Dict[Card, bool]
	solution: Solution

	def __init__(self):
		self.log_book = dict()
		self.solution = Solution(None, None, None)

		for card in Deck.make_deck():
			self.log_book[card] = False

	def log(self, card: Card):
		self.log_book[card] = True
		self.find_solution()

	## maybe store these as list so we don't need to loop every time
	def get(self, card_type: CardType, known: bool) -> List[Card]:
		list = []

		for entry in self.log_book.items():
			if entry[0].type == card_type and entry[1] == known:
				list.append(entry[0])

		return list

	def find_solution(self):
		if self.solution.is_complete():
			return

		if self.solution.character is None:
			remaining = self.get(CardType.CHARACTER, False)
			if len(remaining) == 1:
				self.solution.character = remaining[0]

		if self.solution.room is None:
			remaining = self.get(CardType.ROOM, False)
			if len(remaining) == 1:
				self.solution.room = remaining[0]

		if self.solution.weapon is None:
			remaining = self.get(CardType.WEAPON, False)
			if len(remaining) == 1:
				self.solution.weapon = remaining[0]

	def has_solution(self) -> bool:
		return self.solution.is_complete()

	def __repr__(self):
		return str(self.log_book)
			
class Player:

	# director: Director
	character: Character
	position: Tuple[int, int]
	hand: Hand
	log_book: LogBook
	room: Room

	def __init__(self):
		self.hand = Hand()
		self.log_book = LogBook()
		self.room = None

	def give_card(self, card: Card):
		self.hand.add(card)
		self.log_book.log(card)

	def show_card(self, guess: Solution) -> Solution:
		match = SolutionMatcher.compare_to_hand(self.hand)

		if match.is_empty():
			return None
		return match

	def make_guess(self):
		guess = Solution(None, None, self.room)
		guess.weapon = self.decide_weapon_guess()
		guess.character = self.decide_character_guess()
				
		match = self.director.make_guess(guess)
		if match is None:
			self.log_book.solution = match

	def take_turn(self):
		if self.log_book.has_solution():
			self.director.make_accusation(self, self.log_book.solution)
			return

		if self.room is None or not self.should_guess():
			self.move(Director.roll())
		else:		
			self.make_guess()				

	def move(self, roll: int):
		raise Exception('Not Implemented')

	def decide_weapon_guess(self):
		raise Exception('Not Implemented')

	def decide_character_guess(self):
		raise Exception('Not Implemented')

	def __repr__(self):
		return str(self.character.name)

class DumbPlayer(Player):

	def __init__(self):
		super().__init__()	

	def decide_weapon_guess(self) -> Card:
		return self.log_book.get(CardType.WEAPON, False)[0]

	def decide_chacter_guess(self) -> Card:
		return self.log_book.get(CardType.CHARACTER, False)[0]

	def move(self, roll: int):
		raise Exception('Not Implemented')	

	def __repr__(self):
		return "Dumb Player: " + super().__repr__()

class Director:

	## static
	def roll() -> int:
		return random.randint(1, 6)

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

	def __init__(self):
		self.winner = None

	def new_game(self, players: List[Player]):
		self._assign_players(players)
		self._setup()
		self._play_game()		

		if self.winner is not None:
			print("Winner is " + str(self.winner))
		else:
			## no more opponents left
			print(str(self.players[0]) + " wins by default")

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
		while not self._end_game():
			for player in self.players:
				player.take_turn()

				if self._end_game():
					return

			break

	def _deal_cards(self, deck):
		i = 0
		num_of_players = len(self.players)

		for card in deck:
			self.players[i].give_card(card)
			i += 1

			if i == num_of_players:
				i = 0

	def _assign_players(self, players: List[Player]):
		self.players = players

		for p in self.players:
			p.director = self

		random.shuffle(self.players)

		order = [
			Character.MISS_SCARLET,
			Character.COLONEL_MUSTARD,
			Character.MRS_WHITE,
			Character.MRS_PEACOCK,
			Character.MR_GREEN,
			Character.PROFESSOR_PLUM
		]

		self.player_by_character = dict()

		i = 0
		for player in self.players:
			player.character = order[i]
			self.player_by_character[order[i]] = player
			i += 1

	## store the order somewhere so it doesn't need to be calculated each time
	def make_guess(self, player: Player, solution: Solution) -> Solution:
		## move the accused player
		self.player_by_character[solution.character.value].room = solution.room.value

		player_index = self.players.index(player)

		## determine the order to ask each player (clockwise around the board)
		if player_index == 0:
			other_players = self.players[1:]
		elif player_index == len(self.players) - 1:
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
		if SolutionMatcher.is_match(self.solution, solution):
			self.winner = player
		else:
			## player loses and doesn't get any more turns
			self.players.remove(player)
	
	def _end_game(self):
		## no winner and at least 2 players
		return self.winner is not None or len(self.players) == 1



players = [
	DumbPlayer(),
	DumbPlayer(),
	DumbPlayer(),
	DumbPlayer(),
	DumbPlayer(),
	DumbPlayer()
]

director = Director()
director.new_game(players);
print(director.solution)

for player in director.players:
	print(player.hand)
	print(player.log_book)
	print("===================")
	  