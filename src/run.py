import time

from grid import clear_screen
from world import World
from processors import *
from components import *
from entities import *


def main():
    world = World()
    world.add_entity(Dorf.init(name="Urist", icon="☺", pos=(0, 0)))
    world.add_entity(Dorf.init(name="Bronzi", icon="☻", pos=(14, 14)))
    used = [(0, 0), (14, 14)]
    # Generate walls
    for i in range(30):
        coords = world.random_coords(used)
        world.add_entity([
            Position(x=coords[0], y=coords[1]),
            Obstacle(is_passable=False),
            Display(icon="█"),
        ])
        used.append(coords)
    # Generate socks
    for i in range(30):
        coords = world.random_coords(used)
        world.add_entity([
            Position(x=coords[0], y=coords[1]),
            Name(name=f"Sock {i+1}"),
            Weight(),
            Stockable(),
            Display(icon="s"),
        ])
        used.append(coords)
    coords = world.random_coords(used)
    world.add_entity([
        Name(name="Sock Stockpile"),
        Inventory(),
        Region(tiles=[coords]),
        Display(icon="@")
    ])
    # Processors
    world.add_processor(TaskProcessor)
    # Various Processors for Tasks
    world.add_processor(StockingProcessor)
    # Finalizing Tasks (Movement, etc)
    world.add_processor(PathfindingProcessor)
    world.add_processor(MovementProcessor)
    world.add_processor(RegionProcessor)
    # NOTE: ALWAYS DO THESE LAST (for now)
    world.add_processor(DisplayProcessor)
    # Toggle this on/off w/ comment to enable debugging
    # world.add_processor(DebugProcessor)
    # world.process()
    for i in range(1000):
        clear_screen()
        world.process()
        time.sleep(0.1)
        # input()


if __name__ == "__main__":
    main()
