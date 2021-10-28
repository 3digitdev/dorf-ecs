from typing import List, Optional, Tuple, Dict, Union
from dataclasses import dataclass as component, field

from base import Entity, Task, HaulStep


@component
class Debug:
    messages: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return "\n".join(self.messages)


@component
class Position:
    x: int
    y: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: Union["Position", Tuple[int, int]]) -> bool:
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return self.x == other[0] and self.y == other[1] if other else False

    def as_tuple(self) -> Tuple[int, int]:
        return self.x, self.y


@component
class Movement:
    speed: int = 1
    target: Optional[Tuple[int, int]] = None
    path: List[Tuple[int, int]] = field(default_factory=list)


@component
class Inventory:
    contents: List[Entity] = field(default_factory=list)


@component
class MaxCarry:
    current_weight: int = 0
    # `max_weight=0` means no maximum -- no reason to have this component if this is 0 otherwise!
    max_weight: int = 0

    def __str__(self) -> str:
        return f"{self.current_weight}/{'∞' if not self.max_weight else self.max_weight}"


@component
class Hauls:
    step: Optional[HaulStep] = None
    item: Optional[Entity] = None
    region: Optional[Entity] = None


@component
class Weight:
    weight: int = 1


@component
class Name:
    name: str


@component
class Display:
    icon: str


@component
class Obstacle:
    is_passable: bool


@component
class Region:
    tiles: List[Tuple[int, int]] = field(default_factory=list)


@component
class Stockable:
    # TODO: This is unused for now -- `Stockable` will just be a flag for Entities
    #       in the meantime!
    region: Optional[int] = None


@component
class Tasked:
    priorities: Dict[Task, int] = field(default_factory=dict)
    current_task: Task = Task.IDLE

    def __init__(self):
        self.priorities = {task: task.value for task in Task}
