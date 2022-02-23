from base import Processor
from components import *


class DisplayProcessor(Processor):
    """
    DEBUGGING PROCESSOR
    This just allows us to display the game grid in the console
    """
    def process(self):
        graph = self.world.build_graph()
        for _, (position, display) in self.world.get_components(Position, Display):
            graph.grid[position.x][position.y].icon = display.icon
        for _, (region, display) in self.world.get_components(Region, Display):
            for x, y in region.tiles:
                graph.grid[x][y].icon = display.icon
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
