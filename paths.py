from definitions import Room
from typing import List, Tuple

spaces = [
	[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], #1
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], #2
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], #3
	[0, 0, 0, 0, 0, 0, 3, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], #4
	[0, 1, 1, 1, 1, 1, 2, 1, 2, 3, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0], #5
	[1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 3, 0, 0, 0, 0, 0, 0], #6
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 3, 3, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 0], #7
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], #8
	[0, 0, 0, 0, 0, 0, 3, 2, 1, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0], #9
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 3, 0, 0, 0, 0, 0, 0], #10
	[0, 0, 0, 3, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #11
	[1, 2, 1, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #12
	[0, 3, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0], #13
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #14
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #16
	[0, 0, 0, 0, 0, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], #16
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0], #17
	[0, 1, 1, 1, 1, 1, 1, 1, 0, 3, 0, 0, 0, 0, 3, 0, 1, 1, 1, 2, 1, 1, 1, 1], #18
	[1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 3, 0, 0, 0, 0], #19
	[0, 0, 0, 0, 3, 2, 1, 2, 3, 0, 0, 0, 0, 0, 0, 3, 2, 1, 0, 0, 0, 0, 0, 0], #20
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #21
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #22
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #23
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], #24
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], #25
	#1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 
]

doors = [
	(Room.CONSERVATORY, 5, 20),	
	(Room.BALLROOM, 9, 20),
	(Room.BALLROOM, 10, 18),
	(Room.BALLROOM, 15, 18),
	(Room.BALLROOM, 15, 20),
	(Room.LIBRARY, 4, 11),
	(Room.LIBRARY, 7, 8),
	(Room.BILLARD_ROOM, 6, 16),
	(Room.BILLARD_ROOM, 2, 13),
	(Room.STUDY, 7, 4),
	(Room.HALL, 10, 5),
	(Room.HALL, 12, 7),
	(Room.HALL, 13, 7),
	(Room.LOUNGE, 18, 6),
	(Room.DINING_ROOM, 18, 10),
	(Room.DINING_ROOM, 17, 13),
	(Room.KITCHEN, 20, 19),
]

shortcuts = [
	(Room.STUDY, Room.KITCHEN),
	(Room.KITCHEN, Room.STUDY),
	(Room.LOUNGE, Room.CONSERVATORY)
	(Room.CONSERVATORY, Room.LOUNGE)
]

class Position:
	x: int
	y: int
	connections: List[Position]

	def __init__(self, x, y, connections=[]):
		self.x = x
		self.y = y
		self.connections = connections

class Door(Position):
	room: Room

	def __init__(self, room: Room, x, y, connections=[]):
		super().__init__(x, y, connections)
		self.room = room

class RoomPath:

	room: Room
	distance: int
	path: List[Tuple[int, int]]

	def __init__(self, room: Room, distance: int, path: List[Tuple[int, int]]):
		self.distance = distance
		self.room = room
		self.path = path

	def compare(self, other) -> int:
		if self.distance > other.distance:
			return 1

		if self.distance == other.distance:
			return 0

		return -1

class Board:

	def path_to_room(x: int, y: int, room: Room) -> RoomPath:
		pass

	def path_to_rooms(x: int, y: int, rooms: List[Room]) -> List[RoomPath]:
		paths = []
		for room in rooms:
			paths.append(path_to_room(x, y, room))

		return paths

	def closest_room(x: int, y: int, rooms: List[Room]) -> RoomPath:
		best_room_path = Board.path_to_room(x, y, rooms[0])
		rooms.pop(0)

		for room in rooms:
			room_path = Board.distance_to_room(x, y, room)
			if best_room_path.compare(room_path) == 1:
				best_room_path = room_path				

		return best_room_path

