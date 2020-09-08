from __future__ import annotations
from definitions import Room
from typing import List, Tuple

board_spaces = [
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

#doors = [
#	(Room.CONSERVATORY, 5, 20),	
#	(Room.BALLROOM, 9, 20),
#	(Room.BALLROOM, 10, 18),
#	(Room.BALLROOM, 15, 18),
#	(Room.BALLROOM, 15, 20),
#	(Room.LIBRARY, 4, 11),
#	(Room.LIBRARY, 7, 8),
#	(Room.BILLARD_ROOM, 6, 16),
#	(Room.BILLARD_ROOM, 2, 13),
#	(Room.STUDY, 7, 4),
#	(Room.HALL, 10, 5),
#	(Room.HALL, 12, 7),
#	(Room.HALL, 13, 7),
#	(Room.LOUNGE, 18, 6),
#	(Room.DINING_ROOM, 18, 10),
#	(Room.DINING_ROOM, 17, 13),
#	(Room.KITCHEN, 20, 19),
#]

doors = dict()
doors[Room.CONSERVATORY] = [(5, 20)]
doors[Room.BALLROOM] = [(9, 20), (10, 18), (15, 18), (15, 20)]
doors[Room.LIBRARY] = [(4, 11), (7, 8)]
doors[Room.BILLARD_ROOM] = [(6, 16), (2, 13)]
doors[Room.STUDY] = [(7, 4)]
doors[Room.HALL] = [(10, 5), (12, 7), (13, 7)]
doors[Room.LOUNGE] = [(18, 6)]
doors[Room.DINING_ROOM] = [(18, 10), (17, 13)]
doors[Room.KITCHEN] = [(20, 19)]

shortcuts = [
	(Room.STUDY, Room.KITCHEN),
	(Room.KITCHEN, Room.STUDY),
	(Room.LOUNGE, Room.CONSERVATORY),
	(Room.CONSERVATORY, Room.LOUNGE)
]

class Position:
	connections: List[Position]

	def __init__(self, connections=[]):
		self.connections = connections

class Door(Position):
	room: Room

	def __init__(self, room: Room, connections: List[Position]):
		super().__init__(connections)
		self.room = room

class Space(Position):
	x: int
	y: int

	def __init__(self, x, y, connections=[]):
		super().__init__(connections)
		self.x = x
		self.y = y		

	def __repr__(self):
		return self.pos_str()

	def pos_str(self):
		return "(" + str(self.x + 1) + "," + str(self.y + 1) + ")"

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

	ROW_MAX = len(board_spaces)
	COL_MAX = len(board_spaces[0])

	BOARD_POSITIONS: List[List[Position]] = None

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

	def find_connections(row: int, col: int) -> List[Tuple[int, int]]:
		if board_spaces[row][col] == 0:
			raise Exception(f"Position (${row},${col}) is not valid")

		possibilities = [
			[row - 1, col],
			[row, col - 1],
			[row, col + 1],
			[row + 1, col],
		]

		## remove items that are out of range
		possibilities = list(filter(lambda x: x[0] >=0 and x[1] >=0 and x[0] < Board.ROW_MAX and x[1] < Board.COL_MAX, possibilities))

		## remove spaces that aren't valid
		if board_spaces[row][col] == 3:
			# only the space with value 2 is valid
			return list(filter(lambda x: board_spaces[x[0]][x[1]] == 2, possibilities))
		elif board_spaces[row][col] == 2:
			# only the space with value 3 is valid
			return list(filter(lambda x: board_spaces[x[0]][x[1]] == 3, possibilities))

		## space values 1 and 2 are valid
		return list(filter(lambda x: board_spaces[x[0]][x[1]] > 0, possibilities))

## create position objects for each
board_positions: List[List[Position]] = []
Board.BOARD_POSITIONS = board_positions

r = 0
for row in board_spaces:		
	board_positions.append([None] * 24)

	c = 0
	for cell in row:
		if cell > 0:
			board_positions[c][r] = Space(r, c)
		c += 1

	r += 1

## find connections for each position
r = 0
for row in board_positions:
	c = 0
	for cell in row:
		if cell is not None:
			connection_coors = Board.find_connections(r, c)
			connections = list(map(lambda coors: board_positions[coors[0]][coors[1]], connection_coors))
			board_positions[c][r].connections = connections
		c += 1

	r += 1

## merge doors within a room to a single connection
study_position = None
kitchen_position = None
lounge_positions = None
conservatory_positions = None


#for door_item in doors.items():
#	connections = []
#	door = Door(door_item[0], connections)

#	for door_pos in door_item[1]:
#		# get the existing space
#		space = board_positions[door_pos[0] - 1][door_pos[1] - 1] #1 based
#		print(f"[{door_pos[0]} - 1][{door_pos[1]} - 1]")
#		# copy the spaces' connections into the door's connections
#		door.connections.extend(space.connections)

#		# replace the space with the door
#		board_positions[door_pos[0] - 1][door_pos[1] - 1] = door  #1 based


#door_positions = list(filter(lambda pos: isinstance(pos, Door), board_positions))
#study_positions = list(filter(lambda door: door.room == Room.STUDY, door_positions))
#kitchen_positions = list(filter(lambda door: door.room == Room.KITCHEN, door_positions))
#lounge_positions = list(filter(lambda door: door.room == Room.LOUNGE, door_positions))
#conservatory_positions = list(filter(lambda door: door.room == Room.CONSERVATORY, door_positions))

#assert len(door_positions) == 9
#assert len(study_positions) == 1
#assert len(kitchen_positions) == 1
#assert len(lounge_positions) == 1
#assert len(conservatory_positions) == 1



if True:
	for row in board_positions:	
		print(row)

	for row in board_positions:	
		for cell in row:
			if cell is not None:
				print(str(cell) + ': ' + str(list(map(lambda conn: conn.pos_str(), cell.connections))))