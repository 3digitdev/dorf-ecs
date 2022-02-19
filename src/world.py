import sys
from random import randint
from typing import Dict, Set, List, Type, Optional, Tuple, Iterable

from a_star import Graph
from base import C, Entity, Processor, MAP_WIDTH, MAP_HEIGHT
from components import Position, Obstacle
from terrain import Terrain


class World:
    components: Dict[Type[C], Set[Entity]] = dict()
    processors: List[Processor] = []
    entities: Dict[Entity, Set[Type[C]]] = dict()
    terrain: Set[Entity] = set()
    next_entity_id: int = 0
    dead_entities: Set[Entity] = set()
    # - Caches - #
    component_cache: Dict[Type[C], List[Tuple[Entity, C]]] = dict()
    multi_component_cache: Dict[List[Type[C]], List[Tuple[Entity, List[C]]]] = dict()
    # - Game Board - #
    rows: int = MAP_HEIGHT
    cols: int = MAP_WIDTH

    # ---- Cleanup Functions ---- #
    def clear_caches(self):
        self.component_cache = {}
        self.multi_component_cache = {}

    # ---- Initialization Functions ---- #
    def init_board(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                self.terrain.add(self.add_entity([Terrain(), Position(x=r, y=c)]))

    def random_coords(self, skip: List[Tuple[int, int]]) -> Tuple[int, int]:
        coords = (randint(0, self.rows - 1), randint(0, self.cols - 1))
        while coords in skip:
            coords = (randint(0, self.rows - 1), randint(0, self.cols - 1))
        return coords

    def get_obstacles(self) -> List[Tuple[int, int]]:
        obstacles: List[Tuple[int, int]] = []
        for _, (position, obstacle) in self.get_components(Position, Obstacle):
            if not obstacle.is_passable:
                obstacles.append((position.x, position.y))
        return obstacles

    def build_graph(self) -> Graph:
        return Graph(self.rows, self.cols)

    # ---- Processing Functions ---- #
    def process(self) -> None:
        self.kill_entities()
        for processor in self.processors:
            processor.process()

    # ---- Entity Functions ---- #
    def add_entity(self, components: List[C]) -> Entity:
        self.next_entity_id += 1
        for comp in components:
            self.add_component(self.next_entity_id, comp)
        return self.next_entity_id

    def remove_entity(self, entity: Entity) -> None:
        self.dead_entities.add(entity)

    def kill_entities(self) -> None:
        self.clear_caches()
        for entity in self.dead_entities:
            # Delete the entity from all component references
            for component_name in self.entities[entity]:
                self.remove_component(entity, component_name)
            del self.entities[entity]
        self.dead_entities.clear()

    def entity_exists(self, entity: Entity) -> bool:
        return entity in self.entities and entity not in self.dead_entities

    # ---- Component Functions ---- #
    def add_component(self, entity: Entity, component: C) -> None:
        cls = component.__class__
        if cls not in self.components:
            self.components[cls] = set()
        self.components[cls].add(entity)
        if entity not in self.entities:
            self.entities[entity] = {}
        self.entities[entity][cls] = component

    def remove_component(self, entity: Entity, component: Type[C]) -> None:
        self.components[component].discard(entity)
        # Remove the component key to save space if its empty
        if not self.components[component]:
            del self.components[component]
        del self.entities[entity][component]
        self.clear_caches()

    def has_component(self, entity: Entity, component: Type[C]) -> bool:
        return entity in self.components[component]

    def _get_component(self, component: Type[C]) -> Iterable[Tuple[Entity, C]]:
        for entity in self.components.get(component, set()):
            yield entity, self.entities[entity][component]

    def get_component(self, component: Type[C]) -> List[Tuple[Entity, C]]:
        try:
            return self.component_cache[component]
        except KeyError:
            # Not in cache yet, add it and return
            result = list(self._get_component(component))
            return self.component_cache.setdefault(component, result)

    def _get_components(self, *components: Type[C]) -> List[Tuple[Entity, List[C]]]:
        try:
            # Some set theory for speed
            for entity in set.intersection(*[self.components[c] for c in components]):
                yield entity, [self.entities[entity][c] for c in components]
        except TypeError:
            print("No components passed to world.get_components()")
            sys.exit(1)
        except KeyError:
            pass

    def get_components(self, *components: Type[C]) -> List[Tuple[Entity, List[C]]]:
        try:
            return self.multi_component_cache[components]
        except KeyError:
            # Not in cache yet, add it and return
            result = list(self._get_components(*components))
            return self.multi_component_cache.setdefault(components, result)

    def get_entity_component(self, entity: Entity, component: Type[C]) -> Optional[C]:
        if entity not in self.entities or component not in self.entities[entity]:
            return None
        return self.entities[entity][component]

    # ---- Processor Functions ---- #
    def add_processor(self, processor: Type[Processor], priority=0) -> None:
        self.processors.append(processor(priority=priority, world=self))
        # Sort by priority high -> low
        self.processors.sort(key=lambda p: p.priority, reverse=True)

    def remove_processor(self, processor: Type[Processor]) -> None:
        self.processors = [p for p in self.processors if not isinstance(p, processor)]

    def get_processor(self, processor: Type[Processor]) -> Optional[Processor]:
        for proc in self.processors:
            if isinstance(proc, processor):
                return proc
        else:
            return None
