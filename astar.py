import heapq
from definitions import Space
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

def heuristic(a: Space, b: Space) -> float:
    return (a.col - b.col) ** 2 + (a.row - b.row) ** 2


def a_star_search(start: Space, goal: Space):
    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from: Dict[Space, Optional[Space]] = {}
    cost_so_far: Dict[Space, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Space = frontier.get()
        
        if current == goal:
            break
        
        for next in current.connections:
            new_cost = cost_so_far[current] + 1

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    shortest_path = []
    prev = goal
    while prev is not None:
        shortest_path.append(prev)
        prev = came_from[prev]

    shortest_path.reverse()

    return shortest_path, cost_so_far[goal]