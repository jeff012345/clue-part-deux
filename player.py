from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional
from definitions import *
from paths import RoomPath, Board
import random
import numpy as np
from threading import Lock

class PlayerAction(Enum):
	ACCUSATION = 1
	GUESS = 2
	MOVE = 3

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

	def has_card(self, card: Card):
		try:
			if card.type == CardType.WEAPON:
				self.weapons.index(card)
			elif card.type == CardType.ROOM:
				self.rooms.index(card)
			elif card.type == CardType.CHARACTER:
				self.characters.index(card)
			return True
		except ValueError:
			return False

	def __repr__(self):
		return str(self.all)

class SolutionMatcher:

	def compare_to_hand(hand: Hand, solution: Solution) -> Solution:
		matches = Solution(None, None, None)

		if hand.has_card(solution.weapon):
			matches.weapon = solution.weapon

		if hand.has_card(solution.room):
			matches.room = solution.room

		if hand.has_card(solution.character):
			matches.character = solution.character

		return matches	

class LogBook:

	log_book: Dict[Card, bool]
	
	weapons: List[np.int32]
	characters: List[np.int32]
	rooms: List[np.int32]

	solution: Solution

	def __init__(self):
		self.log_book = dict()
		self.solution = Solution(None, None, None)

		self.weapons = np.zeros((6,), dtype=np.float64)
		self.characters = np.zeros((6,), dtype=np.float64)
		self.rooms = np.zeros((9,), dtype=np.float64)

		for card in Deck.static_deck:
			self.log_book[card] = False

	def log(self, card: Card):
		if card is None:
			return

		self.log_book[card] = True
		self.find_solution(card.type)

		index = card.value.value - 1

		if card.type == CardType.WEAPON:
			self.weapons[index] = 1
		elif card.type == CardType.CHARACTER:
			self.characters[index] = 1
		else:
			self.rooms[index] = 1

	## maybe store these as list so we don't need to loop every time
	def get(self, card_type: CardType, known: bool) -> List[Card]:
		list = []

		for entry in self.log_book.items():
			if entry[0].type == card_type and entry[1] == known:
				list.append(entry[0])

		return list

	def find_solution(self, card_type: CardType):
		if self.solution.is_complete():
			return

		if card_type == CardType.CHARACTER and self.solution.character is None:
			remaining = self.get(CardType.CHARACTER, False)
			if len(remaining) == 1:
				self.solution.character = remaining[0]

		if card_type == CardType.ROOM and self.solution.room is None:
			remaining = self.get(CardType.ROOM, False)
			if len(remaining) == 1:
				self.solution.room = remaining[0]

		if card_type == CardType.WEAPON and self.solution.weapon is None:
			remaining = self.get(CardType.WEAPON, False)
			if len(remaining) == 1:
				self.solution.weapon = remaining[0]

	def has_solution(self) -> bool:
		return self.solution.is_complete()

	def is_room_known(self, room: Room) -> bool:
		room_card = Card(room, CardType.ROOM)
		return self.log_book[room_card]

	def found_solution(self, solution: Solution):
		if self.solution.character is None and not self.log_book[solution.character]:
			self.solution.character = solution.character			
			self.characters = np.ones((6,), dtype=np.int32)
			self.characters[solution.character.value.value - 1] = 0

		if self.solution.weapon is None and not self.log_book[solution.weapon]:
			self.solution.weapon = solution.weapon
			self.weapons = np.ones((6,), dtype=np.int32)
			self.weapons[solution.character.value.value - 1] = 0

		if self.solution.room is None and not self.log_book[solution.room]:
			self.solution.room = solution.room
			self.rooms = np.ones((9,), dtype=np.int32)
			self.rooms[solution.character.value.value - 1] = 0

	def __repr__(self):
		return str(self.log_book)

class Player:
	director: Director
	character: Character
	position: Tuple[int, int]
	board_position: Position
	hand: Hand
	log_book: LogBook
	room: Room

	def __init__(self):
		pass

	def pick_card_to_show(self, match: Solution, guess: Solution) -> Solution:
		raise Exception('Not Implemented')

	def take_turn(self, action: PlayerAction = None):		
		raise Exception('Not Implemented')

	def reset(self):
		self.hand = Hand()
		self.log_book = LogBook()
		self.room = None		
		self.position = None
		self.board_position = None
		self.character = None

	# deal card to player
	def give_card(self, card: Card):
		self.hand.add(card)
		self.log_book.log(card)

	# player has to decide which card to show to the guesser
	def show_card(self, guess: Solution) -> Solution:
		match = SolutionMatcher.compare_to_hand(self.hand, guess)

		if match.is_empty():
			return None

		return self.pick_card_to_show(match, guess)

	def move_path(self, roll: int, room_path: RoomPath):
		if roll < room_path.distance:
			raise Exception("Path is longer than roll")

		for p in room_path.path:
			self.move(p)
	
	def move(self, p: Position):
		self.board_position = p

		if isinstance(p, Space):
			self.room = None
			self.position = (p.row, p.col)
		elif isinstance(p, RoomPosition):
			self.enter_room(p.room)
		else:
			raise Expection("wat?")

	def enter_room(self, room: Room):
		self.room = room
		self.position = None

	def __repr__(self):
		return str(self.character.name)

class NaiveComputerPlayer(Player):

	remaining_path: RoomPath

	def __init__(self):
		super().__init__()	
		self.remaining_path = None

	def enter_room(self, room):
		super().enter_room(room)
		self.remaining_path = None

	def pick_card_to_show(self, match: Solution, guess: Solution) -> Solution:
		# only have to show one card
		if match.character is not None:
			match.weapon = None
			match.room = None
		elif match.weapon is not None:
			match.character = None
			match.room = None
		else:
			match.weapon = None
			match.character = None

		return match

	def make_guess(self):
		#print("Making a guess")
		guess = Solution(None, None, Card(self.room, CardType.ROOM))
		guess.weapon = self.decide_weapon_guess()
		guess.character = self.decide_character_guess()

		(match, skipped_count, showing_player) = self.director.make_guess(self, guess)
		self._log_guess_match(guess, match, skipped_count)

	def _log_guess_match(self, guess, match, skipped_count):
		if match is None:
			#print("solution found!")
			self.log_book.found_solution(guess)
		else:
			self.log_book.log(match.character)
			self.log_book.log(match.weapon)
			self.log_book.log(match.room)

	# override
	def take_turn(self, action: PlayerAction = None):
		#print("NaiveComputerPlayer: " + str(self.character) + " taking turn")
		action = action if action is not None else self.next_turn_action()

		if action == PlayerAction.ACCUSATION:
			self.director.make_accusation(self, self.log_book.solution)
		elif action == PlayerAction.MOVE:
			roll = roll_dice()
			path = self.use_roll(roll)
			self.move_path(roll, path)
		else:
			self.make_guess()

	def next_turn_action(self):
		if self.log_book.has_solution():
			return PlayerAction.ACCUSATION

		if self.room is None or not self.should_guess_current_room():
			return PlayerAction.MOVE

		return PlayerAction.GUESS

	def decide_weapon_guess(self) -> Card:
		if self.log_book.solution.weapon is not None:
			return self.log_book.solution.weapon

		return random.choice(self.log_book.get(CardType.WEAPON, False))

	def decide_character_guess(self) -> Card:
		if self.log_book.solution.character is not None:
			return self.log_book.solution.character
		
		return random.choice(self.log_book.get(CardType.CHARACTER, False))

	def should_guess_current_room(self) -> bool:
		# if the room is known, move to another unless all rooms are known
		return not self.log_book.is_room_known(self.room) \
			or (self.log_book.solution.room is not None and self.hand.has_card(Card(self.room, CardType.ROOM)))

	def use_roll(self, roll: int) -> RoomPath:
		if self.remaining_path is not None:
			return self._use_remaining_roll(roll)

		# get all unknown rooms
		unknown_rooms = self._get_unknown_rooms()

		# find the closest unknown room
		room_paths = None
		if self.room is None:
			room_paths = Board.room_paths_from_position(self.position[0], self.position[1], unknown_rooms)
		else:
			room_paths = Board.room_paths_from_room(self.room, unknown_rooms)
		
		path = random.choice(room_paths)

		if path.distance > roll:
			# continue on the next turn
			self.remaining_path = RoomPath(path.room, path.path[roll:])

			path = RoomPath(path.room, path.path[:roll])		

		return path

	def _get_unknown_rooms(self) -> List[Room]:
		return list(map(lambda c: c.value, self.log_book.get(CardType.ROOM, False)))

	def _use_remaining_roll(self, roll):
		if self.remaining_path.distance > roll:
			room = self.remaining_path.room
			this_path = self.remaining_path.path[:roll]
			remaining_path = self.remaining_path.path[roll:]

			self.remaining_path = RoomPath(room, remaining_path)
			return RoomPath(room, this_path)
		else:
			path = self.remaining_path
			self.remaining_path = None
			return path				

	def __repr__(self):
		return "Computer Player: " + super().__repr__()


class Interaction:
	pass

class PickMatchTurn(Interaction):
	match: Solution
	guess: Solution

	def __init__(self, match: Solution, guess: Solution):
		self.match = match
		self.guess = guess

class GuessOutcome(Interaction):
	match: Solution
	showing_player: Player

	def __init__(self, match: Solution, showing_player: Player):
		self.match = match
		self.showing_player = showing_player

class AccusationOutcome(Interaction):
	correct: bool
	solution: Solution

	def __init__(self, correct: bool, solution: Solution):
		self.correct = correct
		self.solution = solution

class OpponentGuess(Interaction):
	opponent: Player
	guess: Solution

	def __init__(self, opponent: Player, guess: Solution):
		self.opponent = opponent
		self.guess = guess

class DealCard(Interaction):
	cards: List[Card]

	def __init__(self, cards: List[Card]):
		self.cards = cards

class OpponentWin(Interaction):
	opponent: Player
	guess: Solution

	def __init__(self, opponent: Player, guess: Solution):
		self.opponent = opponent
		self.guess = guess

class GameOver(Interaction):
	winner: Player
	solution: Solution

	def __init__(self, winner: Player, solution: Solution):
		self.winner = winner
		self.solution = solution

class HumanPlayer(Player):

	on_turn: Callable[[Interaction]]
	_turn_lock: Lock

	card_to_show: Solution

	player_action: PlayerAction
	solution: Solution	

	def __init__(self, turn_lock):
		self.accusation = None
		self.guess = None
		self._turn_lock = turn_lock

	# override
	def show_card(self, guess: Solution) -> Solution:
		self.card_to_show = None
		return super().show_card(guess)

	def pick_card_to_show(self, match: Solution, guess: Solution) -> Solution:
		self.card_to_show = Solution(None, None, None)
		self.on_turn(PickMatchTurn(match, guess))
		return self.card_to_show		

	def set_card_to_show(self, card):
		if card.type == CardType.ROOM:
			self.card_to_show.room = card
		elif card.type == CardType.WEAPON:
			self.card_to_show.weapon = card
		elif card.type == CardType.CHARACTER:
			self.card_to_show.character = card

	def take_turn(self, action: PlayerAction = None):
		print("HumanPlayer: " + str(self.character) + " taking turn")
		self.player_action = None
		self.solution = None

		self.on_turn(Interaction())

		self._wait_for_user()

		if self.player_action == PlayerAction.GUESS:
			(match, skipped, showing_player) = self.director.make_guess(self, self.solution)
			self.on_turn(GuessOutcome(match, showing_player))
			self._wait_for_user()

		elif self.player_action == PlayerAction.ACCUSATION:
			correct = self.director.make_accusation(self, self.solution)
			self.on_turn(AccusationOutcome(correct, self.solution))
			self._wait_for_user()

	def _wait_for_user(self):
		# wait for other thread to get it. probably not needed
		while not self._turn_lock.locked():
			pass

		self._turn_lock.acquire()
		self._turn_lock.release()

	def accuse(self, solution: Solution):
		self.player_action = PlayerAction.ACCUSATION
		self.solution = solution

	def make_guess(self, solution: Solution):
		self.player_action = PlayerAction.GUESS
		self.solution = solution		
	
	# override
	def move(self, position):
		super().move(position)
		self.player_action = PlayerAction.MOVE