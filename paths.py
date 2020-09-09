from __future__ import annotations
from definitions import Room
from typing import List, Tuple
from itertools import chain

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
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #15
	[0, 0, 0, 0, 0, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], #16
	[0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0], #17
	[0, 1, 1, 1, 1, 1, 1, 1, 0, 3, 0, 0, 0, 0, 3, 0, 1, 1, 1, 2, 1, 1, 1, 1], #18
	[1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 3, 0, 0, 0, 0], #19
	[0, 0, 0, 0, 3, 2, 1, 2, 3, 0, 0, 0, 0, 0, 0, 3, 2, 1, 0, 0, 0, 0, 0, 0], #20
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #21
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #22
	[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], #23
	[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], #24
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]  #25
	#1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 
]

doors = dict()
doors[Room.CONSERVATORY] = [(20, 5)]
doors[Room.BALLROOM] = [(20, 9), (18, 10), (18, 15), (20, 16)]
doors[Room.LIBRARY] = [(11, 4), (9, 7)]
doors[Room.BILLARD_ROOM] = [(16, 6), (13, 2)]
doors[Room.STUDY] = [(4, 7)]
doors[Room.HALL] = [(5, 10), (7, 12), (7, 13)]
doors[Room.LOUNGE] = [(6, 18)]
doors[Room.DINING_ROOM] = [(10, 18), (13, 17)]
doors[Room.KITCHEN] = [(19, 20)]

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
			board_positions[r][c] = Space(r, c)
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
			board_positions[r][c].connections = connections
		c += 1

	r += 1

## merge doors within a room to a single connection
for door_item in doors.items():
	connections = []
	door = Door(door_item[0], connections)

	for door_pos in door_item[1]:
		## get the existing space
		space = board_positions[door_pos[0] - 1][door_pos[1] - 1] #1 based
		#print(f"[{door_pos[0]} - 1][{door_pos[1]} - 1]")

		## copy the spaces' connections into the door's connections
		door.connections.extend(space.connections)

		## replace the space with the door
		board_positions[door_pos[0] - 1][door_pos[1] - 1] = door  #1 based

## find the rooms with shortcuts
door_positions = set(filter(lambda pos: isinstance(pos, Door) is True, chain.from_iterable(board_positions)))
study_door = next(door for door in door_positions if door.room == Room.STUDY)
kitchen_door = next(door for door in door_positions if door.room == Room.KITCHEN)
lounge_door = next(door for door in door_positions if door.room == Room.LOUNGE)
conservatory_door = next(door for door in door_positions if door.room == Room.CONSERVATORY)

## add the shortcuts
study_door.connections.append(kitchen_door)
kitchen_door.connections.append(study_door)
lounge_door.connections.append(conservatory_door)
conservatory_door.connections.append(lounge_door)

if True:
	for row in board_positions:	
		print(row)

	def pos_to_str(p: Position):
		if isinstance(p, Space):
			return str(p.pos_str())
		elif isinstance(p, Door):
			return str(p.room)
		return str(p)

	for row in board_positions:	
		for cell in row:
			if cell is not None:
				print(str(cell) + ': ' + str(list(map(pos_to_str, cell.connections)))) 









