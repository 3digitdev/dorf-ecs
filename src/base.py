from abc import abstractmethod
from typing import Any, TypeVar

Entity = int
C = TypeVar('C')
MAP_WIDTH = 15
MAP_HEIGHT = 15


class Processor:
    priority: int
    world: Any

    def __init__(self, priority, world):
        self.priority = priority
        self.world = world

    @abstractmethod
    def process(self):
        raise NotImplementedError
