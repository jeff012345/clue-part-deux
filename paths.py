from __future__ import annotations
from definitions import *
from typing import List, Tuple
from itertools import chain
from astar import a_star_search

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
	[0, 2, 1, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], #12
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
#[(15,7), (15,8), (16,8), (17,8), (17,7), (18,7), (18,6), (18,5)]
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

class Path:
	distance: int
	path: List[Position]

	def __init__(self, path: List[Space]):
		self.distance = len(path)		
		self.path = path

	def compare_dist(self, other) -> int:
		if self.distance > other.distance:
			return 1

		if self.distance == other.distance:
			return 0

		return -1

class RoomPath(Path):
	room: Room
	
	def __init__(self, room: Room, path: List[Space]):
		super().__init__(path)
		self.room = room

class Board:

	ROW_MAX = len(board_spaces)
	COL_MAX = len(board_spaces[0])

	BOARD_POSITIONS: List[List[Position]] = None
	ROOM_POSITIONS: Dict[Room, RoomPosition] = None

	def room_paths_from_position(row: int, col: int, rooms: List[Room]) -> List[RoomPath]:
		start = Board.BOARD_POSITIONS[row][col]

		paths: List[RoomPath] = []
		for room in rooms:
			goal = Board.ROOM_POSITIONS[room]
			path = Board.find_path(start, goal)
			room_path = RoomPath(room, path.path)
			paths.append(room_path)

		return paths

	def room_paths_from_room(start: Room, rooms: List[Room]) -> RoomPath:
		print("Find path from" + str(start) + " to " + str(rooms))
		return list(map(lambda goal: Board.path_from_room_to_room(start, goal), rooms));

	def path_from_room_to_room(start: Room, goal: Room) -> RoomPath:
		start = Board.ROOM_POSITIONS[start]
		goal = Board.ROOM_POSITIONS[goal]

		path = Board.find_path(start, goal)
		room_path = RoomPath(goal, path.path)
		return room_path

	def find_path(start: Position, goal: Position) -> Path:
		shortest_path = a_star_search(start, goal)
		shortest_path.pop(0) #remove the start Position

		return Path(shortest_path)

def find_connections(row: int, col: int) -> List[Tuple[int, int]]:
	if board_spaces[row][col] == 0:
		raise Exception(f"Position (${row},${col}) is not valid")

	possibilities = [
		[row - 1, col],
		[row, col - 1],
		[row, col + 1],
		[row + 1, col]
	]

	## remove items that are out of range
	possibilities = list(filter(lambda x: x[0] >=0 and x[1] >=0 and x[0] < Board.ROW_MAX and x[1] < Board.COL_MAX, possibilities))

	## remove spaces that aren't valid
	if board_spaces[row][col] == 3:
		# only the space with value 2 is valid
		return list(filter(lambda x: board_spaces[x[0]][x[1]] == 2, possibilities))
	elif board_spaces[row][col] == 2:
		## all spaces are valid
		return list(filter(lambda x: board_spaces[x[0]][x[1]] > 0, possibilities))

	# board_spaces[row][col] == 1, only 1 and 2 are valid
	return list(filter(lambda x: board_spaces[x[0]][x[1]] == 1 or board_spaces[x[0]][x[1]] == 2, possibilities))

def find_room_for_door_position():
	#not needed
	pass

## create position objects for each
board_positions: List[List[Position]] = []
Board.BOARD_POSITIONS = board_positions
Board.ROOM_POSITIONS = dict()

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
			space = board_positions[r][c]
			connection_coors = find_connections(r, c)
			connections = list(map(lambda coors: board_positions[coors[0]][coors[1]], connection_coors))
			space.connections = connections
		c += 1

	r += 1

## merge doors within a room to a single connection
for door_item in doors.items():
	connections = []
	door = RoomPosition(door_item[0], connections)
	Board.ROOM_POSITIONS[door.room] = door

	for door_pos in door_item[1]:
		## get the existing space
		space = board_positions[door_pos[0] - 1][door_pos[1] - 1] #1 based
		#print(f"[{door_pos[0]} - 1][{door_pos[1]} - 1]")

		## copy the spaces' connections into the door's connections
		door.connections.extend(space.connections)

		## change the space reference to the door reference in all connection's connections
		for space_conn in space.connections:
			space_conn.connections.remove(space)
			space_conn.connections.append(door)

		## replace the space with the door in the board
		board_positions[door_pos[0] - 1][door_pos[1] - 1] = door  #1 based

## find the rooms with shortcuts
door_positions = set(filter(lambda pos: isinstance(pos, RoomPosition) is True, chain.from_iterable(board_positions)))
study_door = next(door for door in door_positions if door.room == Room.STUDY)
kitchen_door = next(door for door in door_positions if door.room == Room.KITCHEN)
lounge_door = next(door for door in door_positions if door.room == Room.LOUNGE)
conservatory_door = next(door for door in door_positions if door.room == Room.CONSERVATORY)

## add the shortcuts
study_door.connections.append(kitchen_door)
kitchen_door.connections.append(study_door)
lounge_door.connections.append(conservatory_door)
conservatory_door.connections.append(lounge_door)

if False:
	for row in board_positions:	
		print(row)

	def pos_to_str(p: Position):
		if isinstance(p, Space):
			return str(p.pos_str())
		elif isinstance(p, RoomPosition):
			return str(p.room)
		return str(p)

	for row in board_positions:	
		for cell in row:
			if cell is not None:
				print(str(cell) + ': ' + str(list(map(pos_to_str, cell.connections)))) 

#start = Board.BOARD_POSITIONS[14][6] #15,7  
#goal = Board.BOARD_POSITIONS[17][1] #18,5

#assert isinstance(start, Space) is True
#assert isinstance(goal, Space) is True

#(came_from, cost_so_far) = a_star_search(start, goal)

#print(came_from)
#print(cost_so_far)


#(1,17) -> study

start = Board.BOARD_POSITIONS[0][16] #(1,17)
goal = Board.ROOM_POSITIONS[Room.STUDY]
#goal = Board.BOARD_POSITIONS[4][6] #(5,7)
path = a_star_search(start, goal)
print(path)
