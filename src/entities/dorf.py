from processors import *


class Dorf:
    @staticmethod
    def init(name: str, icon: str, pos: Tuple[int, int], carry: int = 5):
        return [
            Name(name=name),
            Position(*pos),
            Movement(),
            Inventory(),
            MaxCarry(max_weight=carry),
            Tasked(),
            # Debug Processors
            Display(icon=icon),
            Debug(),
        ]
