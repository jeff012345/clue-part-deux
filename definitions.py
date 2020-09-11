from __future__ import annotations
from enum import Enum
from typing import List, Tuple

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

class Character(Enum):
	MRS_WHITE = 1
	MRS_PEACOCK = 2
	MISS_SCARLET = 3
	COLONEL_MUSTARD = 4
	MR_GREEN = 5
	PROFESSOR_PLUM = 6

class Weapon(Enum):
	CANDLESTICK = 1
	REVOLVER = 2
	ROPE = 3
	WRENCH = 4
	LEAD_PIPE = 5
	KNIFE = 6

class CardType(Enum):
	ROOM = 1
	CHARACTER = 2
	WEAPON = 3

class Position:
	connections: List[Position]

	def __init__(self, connections=[]):
		self.connections = connections

class Door(Position):
	room: Room

	def __init__(self, room: Room, connections: List[Position]):
		super().__init__(connections)
		self.room = room

	def __repr__(self):
		return str(self.room) + "; " + str(self.connections)

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

	#def __eq__(self, value):
	#	return self.row == value.row and self.col == value.col

	#def __ne__(self, value):
	#	return self.row != value.row or self.col != value.col

	#def __lt__(self, obj):
	#	return False

	#def __le__(self, obj):
	#	return False

	#def __gt__(self, obj):
	#	return True

	#def __ge__(self, obj):
	#	return True

	#def __hash__(self):
	#	return int.__hash__(self.row) + int.__hash__(self.col)