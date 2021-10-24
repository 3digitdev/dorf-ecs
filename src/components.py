from typing import List, Optional, Tuple
from dataclasses import dataclass as component, field

from base import Entity


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
    region: Optional[int]
