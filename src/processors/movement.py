from a_star import Graph, find_path
from base import Processor
from components import *


class MovementProcessor(Processor):
    """
    What it sounds like -- handles movement of any entity that can move.  Uses the target/path for
    determining where to move to next.
    """
    def process(self):
        obstacles = self.world.get_obstacles()
        for _, (position, movement, name, debug) in self.world.get_components(Position, Movement, Name, Debug):
            debug.messages.append(f"Processing movement for {name.name}: {movement}")
            if not movement.target:
                movement.path = []
                continue
            else:  # Move along path at specified speed
                for i in range(movement.speed):
                    if not movement.path:
                        break
                    next_step = movement.path.pop(0)
                    if next_step in obstacles:
                        # The terrain changed, and we don't have a valid path anymore.
                        # Clear out the invalid path so the PathfindingProcessor can give us a new one
                        movement.path = []
                        # We don't want to hit the `if` at the end
                        break
                    else:
                        debug.messages.append(f"{name.name} moving to {next_step}")
                        position.x, position.y = next_step
                # Check if they reached their destination
                if not movement.path:
                    movement.target = None


class PathfindingProcessor(Processor):
    """
    Handles setting up any Entity that can move.  If the Entity has a target location,
    This will find it a path and give it out so it can follow it in subsequent ticks.
    """
    def _build_graph(self) -> Graph:
        obstacles = self.world.get_obstacles()
        # Build a graph from them
        graph = self.world.build_graph()
        for x, y in obstacles:
            graph.grid[x][y].obstacle = True
        return graph

    def process(self):
        # Don't immediately build the graph just in case we don't actually need it
        graph: Optional[Graph] = None
        # Apply pathfinding and process movement
        for _, (position, movement, debug) in self.world.get_components(Position, Movement, Debug):
            if not movement.target:
                continue
            if not movement.path:
                debug.messages.append(f"Finding path to {movement.target}")
                # We do need the graph now
                graph = self._build_graph() if not graph else graph
                movement.path = find_path(
                    graph, position.x, position.y, movement.target[0], movement.target[1]
                )
                if not movement.path:
                    movement.path = []
                    movement.target = None
                    debug.messages.append(f"No path to target at {position}")
