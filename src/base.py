from abc import abstractmethod
from enum import Enum, IntEnum, auto
from typing import Any, TypeVar

Entity = int
C = TypeVar('C')
MAP_WIDTH = 15
MAP_HEIGHT = 15


class HaulStep(Enum):
    NEED_ITEM = auto()
    FIND_ITEM = auto()
    NEED_REGION = auto()
    FIND_REGION = auto()


class Task(IntEnum):
    """The values of these represent their default priority"""
    IDLE = 0
    HAUL = 1


class Processor:
    priority: int
    world: Any

    def __init__(self, priority, world):
        self.priority = priority
        self.world = world

    @abstractmethod
    def process(self):
        raise NotImplementedError
