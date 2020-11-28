from __future__ import annotations
from enum import Enum
from typing import List, Tuple
import random

def roll_dice() -> int:
	return random.randint(1, 6)

def pretty_print_enum(enum: Enum):
	return " ".join(list(map(lambda s: s.lower().capitalize(), enum.name.split("_"))))

class Room(Enum):
	STUDY = 1
	LIBRARY = 2
	CONSERVATORY = 3
	HALL = 4
	KITCHEN = 5
	BALLROOM = 6
	DINING_ROOM = 7
	LOUNGE = 8
	BILLARD_ROOM = 9

	def pretty(self):
		return pretty_print_enum(self)

class Character(Enum):
	MRS_WHITE = 1
	MRS_PEACOCK = 2
	MISS_SCARLET = 3
	COLONEL_MUSTARD = 4
	MR_GREEN = 5
	PROFESSOR_PLUM = 6

	def pretty(self):
		return pretty_print_enum(self)

class Weapon(Enum):
	CANDLESTICK = 1
	REVOLVER = 2
	ROPE = 3
	WRENCH = 4
	LEAD_PIPE = 5
	KNIFE = 6

	def pretty(self):
		return pretty_print_enum(self)

class CardType(Enum):
	ROOM = 1
	CHARACTER = 2
	WEAPON = 3

	def pretty(self):
		return pretty_print_enum(self)

class Position:
	connections: List[Position]

	def __init__(self, connections=[]):
		self.connections = connections

class RoomPosition(Position):
	room: Room

	def __init__(self, room: Room, connections: List[Position]):
		super().__init__(connections)
		self.room = room

	def __repr__(self):
		return str(self.room) ## + "; " + str(self.connections)

	def __eq__(self, other):
		if isinstance(other, RoomPosition):
			return self.room == other.room
		return False

	def __ne__(self, other):
		"""Overrides the default implementation (unnecessary in Python 3)"""
		x = self.__eq__(other)
		if x is not NotImplemented:
			return not x
		return NotImplemented

	def __hash__(self):
		return super().__hash__()

class Space(Position):
	row: int
	col: int

	def __init__(self, row, col, connections=[]):
		super().__init__(connections)
		self.row = row
		self.col = col	

	def __repr__(self):
		return self.pos_str()

	def pos_str(self):
		return "(" + str(self.row + 1) + "," + str(self.col + 1) + ")"

	def __eq__(self, other):
		if isinstance(other, Space):
			return self.row == other.row and self.col == other.col
		return False

	def __ne__(self, other):
		"""Overrides the default implementation (unnecessary in Python 3)"""
		x = self.__eq__(other)
		if x is not NotImplemented:
			return not x
		return NotImplemented

	def __hash__(self):
		return super().__hash__()

class Card:

	value: Enum
	type: CardType

	def __init__(self, value: Enum, type: CardType):
		self.value = value
		self.type = type

	def __str__(self):
		return self.value.pretty()

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
		c = 'None' if self.character is None else self.character.value.pretty()
		r = 'None' if self.room is None else self.room.value.pretty()
		w = 'None' if self.weapon is None else self.weapon.value.pretty()
		return c + " in the " + r + " with the " + w

	def is_match(self, other: Solution):
		return self.weapon == other.weapon and self.room == other.room and self.character == other.character

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
			Card(Weapon.KNIFE, CardType.WEAPON)
		]

	static_deck = make_deck()