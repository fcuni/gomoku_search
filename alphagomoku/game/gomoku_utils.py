from dataclasses import dataclass
from enum import Enum


class PlayerEnum(Enum):
    BLACK = "B"
    WHITE = "W"


class StartingRule(Enum):
    BASIC = "Basic"
    SWAP = "Swap"
    SWAP2 = "Swap2"


@dataclass
class GridPosition:
    x: int
    y: int

    def __call__(self):
        return self.x, self.y


@dataclass
class Move:
    player: PlayerEnum
    position: GridPosition

    def to_dict(self):
        return {"player": self.player.value, "position": self.position()}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(PlayerEnum(data["player"]), GridPosition(*data["position"]))


class GomokuCell:

    def __init__(self):
        self._current_player: PlayerEnum | None = None

    def get_player(self):
        return self._current_player

    def set_player(self, player: PlayerEnum):
        assert self._current_player is None, "Cell is already occupied"
        self._current_player = player


class GomokuBoard:

    def __init__(self, w_size: int = 15, h_size: int = 15):
        self._w_size = w_size
        self._h_size = h_size
        self._board: list[list[GomokuCell]] = [[GomokuCell() for _ in range(self._w_size)] for _ in range(self._h_size)]

    def __getitem__(self, position: GridPosition) -> GomokuCell:
        pos_x, pos_y = position()
        return self._board[pos_x][pos_y]

    @property
    def size(self):
        return self._w_size, self._h_size

    def _check_valid_move(self, move: Move):
        position_x, position_y = move.position()
        assert (0 <= position_x <= self._w_size), f"Move x-value must be between 0 and {self._w_size}, got {position_x}"
        assert (0 <= position_y <= self._h_size), f"Move y-value must be between 0 and {self._h_size}, got {position_y}"
        assert self[move.position].get_player() is None, "Cell is already occupied"

    def make_move(self, move: Move):
        self._check_valid_move(move)
        self[move.position].set_player(move.player)

    def _get_board_state_string(self) -> str:
        """Utility method to display the board for debugging purposes."""

        board_str = ""

        def cell_repr(cell: GomokuCell):
            return " " if not cell.get_player() else cell.get_player().value

        horizontal_line = "=" * (17 * 4)
        column_numbers = "   " + "".join(f" {i:2} " for i in range(15))

        board_str += column_numbers + "\n"
        board_str += horizontal_line + "\n"
        for i, row in enumerate(self._board):
            row_repr = " | ".join(cell_repr(cell) for cell in row)
            board_str += f"{i:2} | {row_repr} | {i:2}\n"
            board_str += horizontal_line + "\n"
        board_str += column_numbers
        return board_str

    def display_board(self):
        print(self._get_board_state_string())

    def store_board(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self._get_board_state_string())
