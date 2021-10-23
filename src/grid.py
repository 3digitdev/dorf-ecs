import time

from typing import List

CLEAR = "\033[2J"
RESET = "\033[0m"
POS = "\033[{row};{col}H"
EMPTY = " "


def printnnl(code: str):
    print(code, end="")


def clear_screen():
    print(RESET)
    print(CLEAR)
    printnnl(POS.format(row=0, col=0))


class Board:
    data: List[List[str]] = []

    def __init__(self, width: int, height: int):
        for r in range(height):
            row = []
            for c in range(width):
                row.append(EMPTY)
            self.data.append(row)

    def set_at(self, row: int, col: int, char: str = EMPTY):
        self.data[row][col] = char

    def __str__(self) -> str:
        rep = ""
        for r in self.data:
            for c in r:
                rep += f"[{c}] "
            rep += "\n"
        return rep


if __name__ == "__main__":
    board = Board(5, 5)
    print(board)
    time.sleep(2)
    clear_screen()
    print("Goodbye")
