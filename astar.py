import heapq
from typing import List
from definitions import RoomPosition, Position
import random
import sys

class PriorityQueue:
    def __init__(self):
        self.elements: Array = []
    
    def empty(self) -> bool:
        return len(self.elements) == 0
    
    def put(self, item, priority: float):
        heapq.heappush(self.elements, (priority, random.randint(1, 9999999999999999), item))
    
    def get(self):
        return heapq.heappop(self.elements)[2]

def heuristic(a: Position, b: Position) -> float:
    if a == b:
        return 0

    if isinstance(a, RoomPosition):
        if isinstance(b, RoomPosition):
            raise Exception("Cannot calculate heuristic between two rooms")
        return 1 # (1^2 + 0^2)

    if isinstance(b, RoomPosition):
        return 1 # (1^2 + 0^2)

    # both are Space
    return (a.col - b.col) ** 2 + (a.row - b.row) ** 2

def a_star_search(start: Position, goal: Position) -> List[Position]:
    if start is None: 
        raise Exception("Start is None")

    if goal is None:
        raise Exception("goal is None")

    if start == goal:
        raise Exception('Start and goal are the same')

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from: Dict[Position, Optional[Position]] = {}
    cost_so_far: Dict[Position, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Position = frontier.get()
        
        if current == goal:
            break
        
        for next in current.connections:
            if isinstance(next, RoomPosition) and next != goal:
                # once you enter a room, it's a dead end
                continue

            new_cost = cost_so_far[current] + 1

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    if frontier.empty():
        print(str(start) + " to " + str(goal))
        raise Exception('no path found')

    shortest_path = []
    prev = goal
    while prev is not None:
        shortest_path.append(prev)
        prev = came_from[prev]

    shortest_path.reverse()

    return shortest_path



