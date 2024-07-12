import json
from dataclasses import dataclass, field

import numpy as np
from game.gomoku_utils import GomokuBoard, GridPosition, Move, PlayerEnum, StartingRule

MoveHistory = list[Move]


@dataclass
class GomokuGameData:
    """Class to store the game data."""
    moves: MoveHistory = field(default_factory=list)
    winner: PlayerEnum | None = None
    winning_move: Move | None = None

    def to_dict(self) -> dict:
        """Convert the game data to a dictionary."""
        return {
            "moves": [move.to_dict() for move in self.moves],
            "winner": self.winner.value if self.winner else None,
            "winning_move": self.winning_move.to_dict() if self.winning_move else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GomokuGameData":
        """Initialise the game data from a dictionary."""
        winner = PlayerEnum(data["winner"]) if data["winner"] else None
        return cls(
            moves=[Move.from_dict(move) for move in data["moves"]],
            winner=winner,
            winning_move=Move.from_dict(data["winning_move"]) if data["winning_move"] else None,
        )


class GomokuGame:
    """Class to represent a game of Gomoku."""
    def __init__(self, starting_rule: StartingRule = StartingRule.BASIC, board_size: int | tuple[int, int] = 15):
        """Initialise the game."""
        self.starting_rule: StartingRule = starting_rule
        self.current_player: PlayerEnum = PlayerEnum.BLACK
        self.is_initialised = False
        self.is_reset = False
        self.board: GomokuBoard = GomokuBoard(size=board_size)
        self._turn = 0

    @property
    def turn(self):
        """Return the current turn number."""
        return self._turn

    def make_move(self, move: Move, dry_run: bool = False) -> bool:
        """Make a move on the board."""
        assert self.is_reset, "Game has not been reset yet"
        if not self.is_initialised and not dry_run:
            self._apply_initial_move_rule(initial_move=[move])
        else:
            self.board.make_move(move)
        if not dry_run:
            self.game_data.moves.append(move)
            if self.check_winner():
                self.game_data.winner = move.player
                self.game_data.winning_move = move
            self.current_player = (PlayerEnum.WHITE if self.current_player == PlayerEnum.BLACK else PlayerEnum.BLACK)
        self._turn += 1
        return self.game_data.winner is not None

    def store_game_data(self, file_path: str = "gamedata.json"):
        """Store the moves of the game as a JSON string."""
        with open(file_path, "w") as f:
            json.dump(self.game_data.to_dict(), f)

    @classmethod
    def replay_game(cls, game_json, print_board: bool = True) -> "GomokuGame":
        """Reproduce the moves from a JSON string produced by `store_game_data`."""
        game = cls()
        game.reset()
        with open(game_json) as f:
            game.game_data = GomokuGameData.from_dict(json.load(f))
        game.board = GomokuBoard()    # Reset the board

        last_move = game.game_data.moves[-1] if game.game_data.moves else None
        for move in game.game_data.moves:
            game.make_move(move, dry_run=True)
        if last_move and last_move.player == PlayerEnum.BLACK:
            game.current_player = PlayerEnum.WHITE
        else:
            game.current_player = PlayerEnum.BLACK
        if print_board:
            game.display_board()
        return game

    def display_board(self):
        """Display the current state of the board."""
        return self.board.display_board()

    def get_available_positions(self) -> list[GridPosition]:
        """Return a list of available moves."""
        return self.board.available_positions

    def get_available_positions_mask(self) -> np.ndarray:
        """Return a mask of available moves."""
        return self.board.get_available_positions_mask()

    def check_winner(self) -> bool:
        """Check if the player has won the game after the last move."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        last_move = self.game_data.moves[-1] if self.game_data.moves else None
        assert last_move, "No moves have been made yet."

        x, y = last_move.position()
        player = last_move.player

        def count_consecutive(d: tuple[int, int]):
            count = 1
            w_size, h_size = self.board.size
            dx, dy = d
            # Check in the positive direction
            for i in range(1, 5):
                nx, ny = x + i * dx, y + i * dy
                if (0 <= nx < w_size and 0 <= ny < h_size and self.board[GridPosition(nx, ny)].get_player() == player):
                    count += 1
                else:
                    break
            # Check in the negative direction
            for i in range(1, 5):
                nx, ny = x - i * dx, y - i * dy
                if (0 <= nx < w_size and 0 <= ny < h_size and self.board[GridPosition(nx, ny)].get_player() == player):
                    count += 1
                else:
                    break
            return count

        for d in directions:
            count = count_consecutive(d)
            if count >= 5:
                return True
        return False

    def reset(self):
        """Reset the game board."""
        # Reset the game so the board can be manipulated
        self.is_reset = True

        self.game_data: GomokuGameData = GomokuGameData()
        self.current_player: PlayerEnum = PlayerEnum.BLACK    # Black starts by default
        # Set the game to uninitialised
        self.is_initialised = False
        self._turn = 0

    def _apply_initial_move_rule(self, initial_move: list[Move]):
        """Apply a move according to the initial rule."""
        if self.starting_rule == StartingRule.BASIC:
            assert len(initial_move) == 1, "Only one move is allowed in the basic rule"
            self.is_initialised = True
            self.board.make_move(initial_move[0])
        elif self.starting_rule == "Swap":
            raise NotImplementedError("Swap rule not implemented")
        elif self.starting_rule == "Swap2":
            raise NotImplementedError("Swap2 rule not implemented")
