from definitions import Room
from typing import List, Tuple

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

