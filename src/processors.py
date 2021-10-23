from components import *
from base import Processor
from a_star import Graph, find_path


class MovementProcessor(Processor):
    def process(self):
        obstacles = self.world.get_obstacles()
        for _, (position, movement, name, debug) in self.world.get_components(Position, Movement, Name, Debug):
            if not movement.target:  # Set a new destination
                movement.target = self.world.random_coords(obstacles)
                movement.path = []
                debug.messages.append(f"{name.name} moving to {movement.target}")
            else:  # Move along path at specified speed
                for i in range(movement.speed):
                    if not movement.path:
                        break
                    position.x, position.y = movement.path.pop(0)
                # Check if they reached their destination
                if not movement.path:
                    movement.target = None


class HaulingProcessor(Processor):
    def process(self):
        # Entities that can carry things
        for _, (position, inventory, name, debug) in self.world.get_components(Position, Inventory, Name, Debug):
            space_empty = True
            # Entities that can be carried
            for item, (i_position, weight, i_name) in self.world.get_components(Position, Weight, Name):
                # Need to be standing on the same tile
                if position.x == i_position.x and position.y == i_position.y:
                    space_empty = False
                    debug.messages.append(f"{name.name} found a {i_name.name}!")
                    if inventory.current_weight + weight.weight > inventory.max_weight:
                        debug.messages.append(f"{name.name} can not fit the {i_name.name} in their inventory!")
                        continue
                    # Move the item into the inventory
                    inventory.contents.append(item)
                    inventory.current_weight += weight.weight
                    # The object is being carried so it no longer has a position of its own
                    self.world.remove_component(item, Position)
                    debug.messages.append(f"{name.name} picked up the {i_name.name}    ({inventory.current_weight}/{inventory.max_weight})")
            if space_empty and inventory.contents:
                drop = inventory.contents.pop()
                inventory.current_weight -= self.world.get_entity_component(drop, Weight).weight
                item_name = self.world.get_entity_component(drop, Name)
                # item is no longer being carried; give it a position again
                self.world.add_component(drop, Position(x=position.x, y=position.y))
                debug.messages.append(f"{name.name} dropped {item_name} at {position}    ({inventory.current_weight}/{inventory.max_weight})")


class PathfindingProcessor(Processor):
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
                # We do need the graph now
                graph = self._build_graph() if not graph else graph
                movement.path = find_path(
                    graph, position.x, position.y, movement.target[0], movement.target[1]
                )
                if not movement.path:
                    movement.path = []
                    movement.target = None
                    debug.messages.append(f"No path to target at {position}")


class DisplayProcessor(Processor):
    def process(self):
        graph = self.world.build_graph()
        for _, (position, display) in self.world.get_components(Position, Display):
            graph.grid[position.x][position.y].icon = display.icon
        print(graph)


class DebugProcessor(Processor):
    def process(self):
        for _, debug in self.world.get_component(Debug):
            print(debug)
            debug.messages = []
