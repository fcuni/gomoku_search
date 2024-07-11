import json
from dataclasses import dataclass, field

from game.gomoku_utils import GomokuBoard, GridPosition, Move, PlayerEnum, StartingRule

MoveHistory = list[Move]


@dataclass
class GomokuGameData:
    moves: MoveHistory = field(default_factory=list)
    winner: PlayerEnum | None = None
    winning_move: Move | None = None

    def to_dict(self) -> dict:
        return {
            "moves": [move.to_dict() for move in self.moves],
            "winner": self.winner.value if self.winner else None,
            "winning_move": self.winning_move.to_dict() if self.winning_move else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GomokuGameData":
        winner = PlayerEnum(data["winner"]) if data["winner"] else None
        return cls(
            moves=[Move.from_dict(move) for move in data["moves"]],
            winner=winner,
            winning_move=Move.from_dict(data["winning_move"]) if data["winning_move"] else None,
        )


class GomokuGame:

    def __init__(self, starting_rule: StartingRule = StartingRule.BASIC):
        self.starting_rule: StartingRule = starting_rule
        self.current_player: PlayerEnum = PlayerEnum.BLACK
        self.is_initialised = False

    def make_move(self, move: Move, dry_run: bool = False) -> bool:
        """Make a move on the board."""
        if not dry_run:
            assert (self.is_initialised), "Game has not been initialised. Please call reset() first."
        self.board.make_move(move)
        if not dry_run:
            self.game_data.moves.append(move)
            if self.check_winner():
                self.game_data.winner = move.player
                self.game_data.winning_move = move
            self.current_player = (PlayerEnum.WHITE if self.current_player == PlayerEnum.BLACK else PlayerEnum.BLACK)
        return self.game_data.winner is not None

    def store_game_data(self, file_path: str = "gamedata.json"):
        """Store the moves of the game as a JSON string."""
        with open(file_path, "w") as f:
            json.dump(self.game_data.to_dict(), f)

    @classmethod
    def replay_game(cls, game_json, print_board: bool = True) -> "GomokuGame":
        """Reproduce the moves from a JSON string."""
        game = cls()
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

    def reset(self, initial_move: Move):
        """Reset the game board."""
        # Initialise the game so the board can be manipulated
        self.is_initialised = True

        self.game_data: GomokuGameData = GomokuGameData()
        self.board: GomokuBoard = GomokuBoard()
        self.current_player: PlayerEnum = PlayerEnum.BLACK    # Black starts by default
        self.rule_stage: int = 0    # To track stages in Swap and Swap2 rule_stage
        self._apply_rule_move(initial_move)

    def _apply_rule_move(self, initial_move: Move):
        """Apply a move according to the initial rule."""
        if self.starting_rule == StartingRule.BASIC:
            self.make_move(initial_move)
        elif self.starting_rule == "Swap":
            raise NotImplementedError("Swap rule not implemented")
        elif self.starting_rule == "Swap2":
            raise NotImplementedError("Swap2 rule not implemented")


if __name__ == "__main__":
    game = GomokuGame()
    game.reset(Move(PlayerEnum.BLACK, GridPosition(0, 0)))
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(1, 1)))
    game.store_game_data()
    game.replay_game("gamedata.json")
