from components import *
from base import Processor
from a_star import Graph, find_path


class DisplayProcessor(Processor):
    """
    DEBUGGING PROCESSOR
    This just allows us to display the game grid in the console
    """
    def process(self):
        graph = self.world.build_graph()
        for _, (position, display) in self.world.get_components(Position, Display):
            graph.grid[position.x][position.y].icon = display.icon
        print(graph)


class DebugProcessor(Processor):
    """
    DEBUGGING PROCESSOR
    This allows us to attach messages to entities to get printed to the console
    BELOW the printed-out game grid.
    """
    def process(self):
        for _, debug in self.world.get_component(Debug):
            print(debug)
            debug.messages = []


class MovementProcessor(Processor):
    """
    What it sounds like -- handles movement of any entity that can move.  Uses the target/path for
    determining where to move to next.
    """
    def process(self):
        obstacles = self.world.get_obstacles()
        for _, (position, movement, name, debug) in self.world.get_components(Position, Movement, Name, Debug):
            # TODO:  TEMPORARY.  This is just randomly assigning a new destination when we run out.
            if not movement.target:  # Set a new destination
                movement.target = self.world.random_coords(obstacles)
                movement.path = []
                debug.messages.append(f"{name.name} moving to {movement.target}")
            else:  # Move along path at specified speed
                for i in range(movement.speed):
                    if not movement.path:
                        break
                    next_step = movement.path.pop(0)
                    if next_step in obstacles:
                        # The terrain changed and we don't have a valid path anymore.
                        # Clear out the invalid path so the PathfindingProcessor can give us a new one
                        movement.path = []
                        # We don't want to hit the `if` at the end
                        continue
                    else:
                        position.x, position.y = next_step
                # Check if they reached their destination
                if not movement.path:
                    movement.target = None


class HaulingProcessor(Processor):
    """
    Handles Entities that can carry items -- picking up and putting down items when applicable.
    THIS WILL CHANGE SIGNIFICANTLY EVENTUALLY.  Right now it's as basic as possible.
    """
    def process(self):
        for _, (position, inventory, carry, name, debug) in self.world.get_components(Position, Inventory, MaxCarry, Name, Debug):
            space_empty = True
            for item, (i_position, weight, i_name) in self.world.get_components(Position, Weight, Name):
                if not (position.x == i_position.x and position.y == i_position.y):
                    continue
                space_empty = False
                debug.messages.append(f"{name.name} found a {i_name.name}!")
                if carry.current_weight + weight.weight > carry.max_weight:
                    debug.messages.append(f"{name.name} can not fit the {i_name.name} in their inventory!")
                    continue
                # Move the item into the inventory
                inventory.contents.append(item)
                carry.current_weight += weight.weight
                # The object is being carried so it no longer has a position of its own
                self.world.remove_component(item, Position)
                debug.messages.append(f"{name.name} picked up the {i_name.name}  ({carry})")
            if space_empty and inventory.contents:
                drop = inventory.contents.pop()
                carry.current_weight -= self.world.get_entity_component(drop, Weight).weight
                item_name = self.world.get_entity_component(drop, Name)
                # item is no longer being carried; give it a position again
                self.world.add_component(drop, Position(x=position.x, y=position.y))
                debug.messages.append(f"{name.name} dropped {item_name.name} at {position}  ({carry})")


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
                # We do need the graph now
                graph = self._build_graph() if not graph else graph
                movement.path = find_path(
                    graph, position.x, position.y, movement.target[0], movement.target[1]
                )
                if not movement.path:
                    movement.path = []
                    movement.target = None
                    debug.messages.append(f"No path to target at {position}")


class RegionProcessor(Processor):
    """
    Handles making sure that items are registered to a Region
    if they are in a valid position to do so.
    """
    def process(self):
        for item, (position, weight, stockable) in self.world.get_components():
            for reg, (region, inventory) in self.world.get_components(Region, Inventory):
                if item in inventory.contents:
                    if (position.x, position.y) not in region.tiles:
                        inventory.contents.remove(item)
                else:
                    if (position.x, position.y) in region.tiles:
                        inventory.contents.append(item)
