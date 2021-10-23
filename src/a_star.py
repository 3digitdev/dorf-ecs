import sys

from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterable

"""
REFERENCES:
    https://www.redblobgames.com/pathfinding/a-star/introduction.html
    https://www.redblobgames.com/pathfinding/grids/algorithms.html
"""


@dataclass
class Node:
    x: int
    y: int
    obstacle: bool = False
    icon: str = "░"

    def __hash__(self):
        return hash(f"{self.x},{self.y}")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return self.icon


class Graph:
    grid: List[List[Node]]

    def __init__(self, rows: int, cols: int) -> None:
        self.grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                row.append(Node(x=r, y=c))
            self.grid.append(row)

    def neighbors(self, node: Node) -> Iterable[Node]:
        """Provides a generator of valid cardinal direction neighbors"""
        for r, c in [(node.x, node.y - 1), (node.x + 1, node.y), (node.x, node.y + 1), (node.x - 1, node.y)]:
            if r >= 0 and c >= 0:
                try:
                    if not self.grid[r][c].obstacle:
                        yield self.grid[r][c]
                except IndexError:
                    continue

    def cost(self, start: Node, end: Node) -> int:
        """TODO:  CHANGE THIS EVENTUALLY TO INCLUDE WEIGHTS FOR MOVEMENT"""
        return 999 if end.obstacle else 1

    def as_node_path(self, path: List[Tuple[int, int]]) -> List[Node]:
        return [self.grid[n[0]][n[1]] for n in path]

    def __str__(self) -> str:
        rep = f"┌{'─' * len(self.grid)}┐\n"
        for r in self.grid:
            rep += "│"
            for c in r:
                rep += str(c)
            rep += "│\n"
        rep += f"└{'─' * len(self.grid)}┘"
        return rep


class PriorityQueue:
    queue: List[Tuple[Node, int]] = []

    def push(self, item: Node, priority: int):
        self.queue.append((item, priority))
        self.queue.sort(key=lambda x: x[1], reverse=True)

    def pop(self) -> Optional[Node]:
        last = self.queue.pop()
        return last[0] if last else None

    def clear(self) -> None:
        self.queue = []

    def empty(self) -> bool:
        return self.queue == []


def heuristic(goal: Node, current: Node) -> int:
    """
    Heuristic function for search algorithm to bias in the direction of the goal
    Currently uses Manhattan Distance between the nodes
    """
    return abs(goal.x - current.x) + abs(goal.y - current.y)


def find_path(graph: Graph, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
    """A* Pathfinding Algorithm"""
    for row in graph.grid:
        for node in row:
            node.icon = "█" if node.obstacle else node.icon
    start = Node(x=start_x, y=start_y)
    end = Node(x=end_x, y=end_y)
    frontier = PriorityQueue()
    frontier.clear()
    frontier.push(start, 0)
    came_from = dict()
    came_from[start] = None
    cost_so_far = dict()
    cost_so_far[start] = 0
    while not frontier.empty():
        current = frontier.pop()
        if current == end:
            break
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(end, next)
                frontier.push(next, priority)
                came_from[next] = current
    path: List[Tuple[int, int]] = [(end.x, end.y)]
    try:
        next = came_from[end]
    except KeyError:
        # FATAL:  No path to the end goal (entity or goal is boxed in!)
        return []
    while next and next != start:
        path.append((next.x, next.y))
        next = came_from[next]
    path.reverse()
    return path
