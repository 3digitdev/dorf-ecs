from a_star import heuristic, Node
from base import Processor
from components import *


class StockingProcessor(Processor):
    """
    Handles assigning Dwarves an item to start hauling to a stockpile

    This is a 5-step process:
    1) No item assigned;    Find the closest one
    2) Item assigned;       Need to move to it and pick it up
    3) Item picked up;      Need to find the closest region to bring it to
    4) Region assigned;     Need to move to it
    5) Region found;        Drop off the item
    """

    def _find_closest_item(self, pos: Position, carry: MaxCarry, stockpiled_items: List[Entity]) -> Tuple[
        Entity, Optional[Position]]:
        closest: Tuple[int, Optional[Position], int] = (-1, None, 999999)
        for item, (i_pos, weight, stockable) in self.world.get_components(Position, Weight, Stockable):
            if item in stockpiled_items:
                continue
            if carry.current_weight + weight.weight > carry.max_weight:
                continue
            dist = heuristic(Node(x=i_pos.x, y=i_pos.y), Node(x=pos.x, y=pos.y))
            if dist < closest[2]:
                closest = (item, i_pos, dist)
        return closest[0], closest[1]

    def _find_closest_region(self, pos: Position) -> Tuple[Entity, Optional[Position]]:
        closest: Tuple[int, Optional[Position], int] = (-1, None, 999999)
        for region, (reg, _) in self.world.get_components(Region, Inventory):
            # Find the closest valid tile within the region
            for (x, y) in reg.tiles:
                dist = heuristic(Node(x=x, y=y), Node(x=pos.x, y=pos.y))
                if dist < closest[2]:
                    closest = (region, Position(x=x, y=y), dist)
        return closest[0], closest[1]

    def _get_stockpiled_items(self) -> List[Entity]:
        stockpiled_items: List[Entity] = []
        for _, (_, inventory) in self.world.get_components(Region, Inventory):
            stockpiled_items.extend(inventory.contents)
            stockpiled_items = list(set(stockpiled_items))
        return stockpiled_items

    def process(self):
        stockpiled_items = None
        for hauler, (pos, movement, inventory, carry, tasked, hauls, name, debug) in self.world.get_components(
                Position, Movement, Inventory, MaxCarry, Tasked, Hauls, Name, Debug
        ):
            if tasked.current_task != Task.HAUL:
                self.world.remove_component(hauler, Hauls)
                continue
            # 1) No item assigned;  Find the closest one
            if hauls.step == HaulStep.NEED_ITEM:
                debug.messages.append(f"{name.name} needs an item")
                if stockpiled_items is None:
                    stockpiled_items = self._get_stockpiled_items()
                item, item_pos = self._find_closest_item(pos, carry, stockpiled_items)
                if inventory.contents:
                    if not item_pos:  # Not full inventory, but also nothing to pick up
                        hauls.step = HaulStep.NEED_REGION
                        continue
                    # Check if there's a region closer than the nearest item
                    region, region_pos = self._find_closest_region(pos)
                    dist_to_region = heuristic(Node(x=pos.x, y=pos.y), Node(x=region_pos.x, y=region_pos.y))
                    dist_to_item = heuristic(Node(x=pos.x, y=pos.y), Node(x=item_pos.x, y=item_pos.y))
                    if dist_to_region < dist_to_item:
                        # Go drop things off first
                        hauls.step = HaulStep.NEED_REGION
                        continue
                else:
                    # No items to drop off, and no items to pick up -- time to do something else?
                    if not item_pos:
                        # TODO:  SOMEHOW CHANGE TO NEXT PRIORITY TASK?
                        continue
                debug.messages.append(f"Found {item} at {item_pos}")
                movement.target = item_pos.as_tuple()
                stockpiled_items.append(item)
                hauls.step = HaulStep.FIND_ITEM
                hauls.items.append(item)
                debug.messages.append(f"Hauling {hauls}")
            # 2) Item assigned; need to move to it and pick it up
            if hauls.step == HaulStep.FIND_ITEM:
                if not hauls.items:
                    hauls.step = HaulStep.NEED_ITEM
                else:
                    item = hauls.items[-1]
                    item_pos = self.world.get_entity_component(item, Position)
                    debug.messages.append(f"{name.name} looking for item at {pos}...")
                    if not item_pos or (pos == movement.target and item_pos != movement.target):
                        debug.messages.append(f"Moved to {item_pos}, where'd it go??")
                        # The item moved since we set it.  Find a new item instead.
                        hauls.items.pop()
                        hauls.step = HaulStep.NEED_ITEM
                        movement.target = None
                        movement.path = []
                        continue
                    if pos == item_pos:
                        # Found the item; standing on it; pick it up.
                        debug.messages.append(f"Arrived at {pos}; picking up {item}")
                        i_weight = self.world.get_entity_component(item, Weight)
                        if carry.current_weight + i_weight.weight > carry.max_weight:
                            hauls.step = HaulStep.NEED_ITEM
                            hauls.items.pop()
                        else:
                            carry.current_weight += i_weight.weight
                            debug.messages.append(f"Adding {item} to inventory!")
                            inventory.contents.append(item)
                            self.world.remove_component(item, Position)
                            if carry.current_weight < carry.max_weight:
                                hauls.step = HaulStep.NEED_ITEM
                            else:
                                hauls.step = HaulStep.NEED_REGION
                        movement.target = None
                        movement.path = []
            # 3) Item picked up; need to find the closest region to bring it to
            if hauls.step == HaulStep.NEED_REGION:
                debug.messages.append(f"{name.name} needs a region")
                region, region_pos = self._find_closest_region(pos)
                debug.messages.append(f"Found {region} at {region_pos}")
                movement.target = region_pos.as_tuple()
                hauls.step = HaulStep.FIND_REGION
                hauls.region = region
            # 4) Region assigned; need to move to it
            if hauls.step == HaulStep.FIND_REGION:
                debug.messages.append(f"{name.name} looking for region tile at {movement.target}")
                if not hauls.region:
                    hauls.step = HaulStep.NEED_ITEM if not hauls.item else HaulStep.NEED_REGION
                else:
                    region = self.world.get_entity_component(hauls.region, Region)
                    if movement.target not in region.tiles:
                        # The region no longer has a tile there, find a new one
                        region, region_pos = self._find_closest_region(pos)
                        movement.target = region_pos.as_tuple()
                        hauls.region = region
                    if pos == movement.target:
                        # 5) Region found; drop off the items
                        for item in hauls.items:
                            debug.messages.append(f"Arrived at {pos}; dropping off {item}")
                            i_weight = self.world.get_entity_component(item, Weight)
                            carry.current_weight -= i_weight.weight
                            inventory.contents.remove(item)
                            self.world.add_component(item, Position(x=pos.x, y=pos.y))
                        hauls.step = HaulStep.NEED_ITEM
                        hauls.items = []
                        movement.target = None
                        movement.path = []


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
