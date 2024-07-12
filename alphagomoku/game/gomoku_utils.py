from dataclasses import dataclass
from enum import Enum


class PlayerEnum(Enum):
    """Enum to represent the player."""
    BLACK = "B"
    WHITE = "W"


class StartingRule(Enum):
    """Enum to represent the starting rule."""
    BASIC = "Basic"
    SWAP = "Swap"
    SWAP2 = "Swap2"


@dataclass
class GridPosition:
    """Data class to represent the position on the game board."""
    x: int
    y: int

    def __call__(self):
        """Return the x, y coordinates of the position."""
        return self.x, self.y


@dataclass
class Move:
    """Data class to represent a move."""
    player: PlayerEnum
    position: GridPosition

    def to_dict(self):
        """Convert the move to a dictionary."""
        return {"player": self.player.value, "position": self.position()}

    @classmethod
    def from_dict(cls, data: dict):
        """Initialise the move from a dictionary."""
        return cls(PlayerEnum(data["player"]), GridPosition(*data["position"]))


class GomokuCell:
    """Class to represent a cell on the game board."""
    def __init__(self):
        """Initialise the cell."""
        self._current_player: PlayerEnum | None = None

    def get_player(self):
        """Return the player controlling the cell."""
        return self._current_player

    def set_player(self, player: PlayerEnum):
        """Set the player controlling the cell. If the cell is already occupied, raise an error."""
        assert self._current_player is None, "Cell is already occupied"
        self._current_player = player


class GomokuBoard:
    """Class to represent the Gomoku game board."""
    def __init__(self, size: int | tuple[int, int] = 15):
        """Initialise the board."""
        if isinstance(size, tuple):
            self._w_size, self._h_size = size
        else:
            self._w_size = self._h_size = size
        self._board: list[list[GomokuCell]] = [[GomokuCell() for _ in range(self._w_size)] for _ in range(self._h_size)]

    def __getitem__(self, position: GridPosition) -> GomokuCell:
        pos_x, pos_y = position()
        return self._board[pos_x][pos_y]

    @property
    def size(self):
        """Return the size of the board."""
        return self._w_size, self._h_size

    def _check_valid_move(self, move: Move):
        """Check if the move is valid. A move is valid if the position is within the board and the cell is not occupied."""
        position_x, position_y = move.position()
        assert (0 <= position_x <= self._w_size), f"Move x-value must be between 0 and {self._w_size}, got {position_x}"
        assert (0 <= position_y <= self._h_size), f"Move y-value must be between 0 and {self._h_size}, got {position_y}"
        assert self[move.position].get_player() is None, "Cell is already occupied"

    def make_move(self, move: Move):
        """Make a move on the board."""
        self._check_valid_move(move)
        self[move.position].set_player(move.player)

    def _get_board_state_string(self) -> str:
        """Utility method to generate the board as string for debugging purposes."""

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
        """Stdout the current state of the board."""
        print(self._get_board_state_string())

    def store_board(self, file_path: str):
        """Store the current state of the board to a file."""
        with open(file_path, "w") as f:
            f.write(self._get_board_state_string())
