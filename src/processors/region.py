from components import *
from base import Processor


class RegionProcessor(Processor):
    """
    Handles making sure that items are registered to a Region
    if they are in a valid position to do so.
    """
    def process(self):
        for item, (position, weight, stockable) in self.world.get_components(Position, Weight, Stockable):
            for reg, (region, inventory) in self.world.get_components(Region, Inventory):
                if item in inventory.contents:
                    if (position.x, position.y) not in region.tiles:
                        inventory.contents.remove(item)
                else:
                    if (position.x, position.y) in region.tiles:
                        inventory.contents.append(item)
