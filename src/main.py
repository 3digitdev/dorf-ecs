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
        Inventory(max_weight=1),
        Name(name="Urist"),
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
    # Generate socks
    for i in range(30):
        coords = world.random_coords(used)
        world.add_entity([
            Position(x=coords[0], y=coords[1]),
            Name(name=f"Sock {i+1}"),
            Weight(),
            Display(icon="s"),
        ])
    # Processors
    world.add_processor(MovementProcessor)
    world.add_processor(HaulingProcessor)
    world.add_processor(PathfindingProcessor)
    # NOTE: ALWAYS DO THESE LAST (for now)
    world.add_processor(DisplayProcessor)
    world.add_processor(DebugProcessor)
    # world.process()
    for i in range(100):
        clear_screen()
        world.process()
        time.sleep(0.5)
