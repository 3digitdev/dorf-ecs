import time

from ecs import World
from grid import clear_screen
from processors import *
from components import *


if __name__ == "__main__":
    world = World()
    world.add_entity([
        Position(0, 0),
        Movement(),
        Inventory(),
        MaxCarry(max_weight=1),
        Name(name="Urist"),
        Tasked(),
        Display(icon="☺"),
        Debug(),
    ])
    used = [(0, 0)]
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
    world.add_processor(DebugProcessor)
    # world.process()
    for i in range(1000):
        clear_screen()
        world.process()
        time.sleep(0.2)
