from typing import List, Set, Dict, Tuple, Optional
from definitions import *
from paths import RoomPath, Board
import random

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

	def is_room_known(self, room: Room) -> bool:
		room_card = Card(room, CardType.ROOM)
		return self.log_book[room_card]

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

		if self.room is None or not self.should_guess_current_room():
			roll = roll_dice()
			path = self.use_roll(roll)
			self.move_path(roll, path)
		else:		
			self.make_guess()				

	def move_path(self, roll: int, room_path: RoomPath):
		if roll < room_path.distance:
			raise Exception("Path is longer than roll")

		for pos in room_path.path:
			self.position = pos
			# move animation!

	def use_roll(self, roll: int) -> RoomPath:
		raise Exception('Not Implemented')

	def decide_weapon_guess(self) -> Card:
		raise Exception('Not Implemented')

	def decide_character_guess(self) -> Card:
		raise Exception('Not Implemented')

	def should_guess_current_room(self) -> bool:
		raise Exception('Not Implemented')

	def __repr__(self):
		return str(self.character.name)

class ComputerPlayer(Player):

	def __init__(self):
		super().__init__()	

	def decide_weapon_guess(self) -> Card:
		# return first unknown weapon
		return self.log_book.get(CardType.WEAPON, False)[0]

	def decide_chacter_guess(self) -> Card:
		# return first unknown character
		return self.log_book.get(CardType.CHARACTER, False)[0]

	def should_guess_current_room(self) -> bool:
		# if the room is known, move to another
		return not self.log_book.is_room_known(self.room)

	def use_roll(self, roll: int) -> RoomPath:
		# get all unknown rooms
		unknown_rooms = list(map(lambda c: c.value, self.log_book.get(CardType.ROOM, False)))

		# find the closest unknown room
		room_paths = None
		if self.room is None:
			room_paths = Board.room_paths_from_position(self.position[0], self.position[1], unknown_rooms)
		else:
			room_paths = Board.room_paths_from_room(self.room, unknown_rooms)
		
		path = random.choice(room_paths)
		if path.distance > roll:
			path = RoomPath(path.room, path.path[:roll])

		return path

	def __repr__(self):
		return "Computer Player: " + super().__repr__()
