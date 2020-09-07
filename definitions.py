from enum import Enum

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
