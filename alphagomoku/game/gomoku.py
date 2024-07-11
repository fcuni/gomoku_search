import json
from dataclasses import dataclass, field

from game.gomoku_utils import GomokuBoard, Move, PlayerEnum, StartingRule

MoveHistory = list[Move]


@dataclass
class GomokuGameData:
    moves: MoveHistory = field(default_factory=list)
    winner: PlayerEnum | None = None


class GomokuGame:
    def __init__(self):
        self.game_data: GomokuGameData = GomokuGameData()
        self.board: GomokuBoard = GomokuBoard()
        self.starting_rule: StartingRule = StartingRule.BASIC
        self.current_player: PlayerEnum = PlayerEnum.BLACK  # Black starts by default
        self.rule_stage: int = 0  # To track stages in Swap and Swap2 rules

    def make_move(self, move: Move) -> bool:
        """Make a move on the board."""
        self.board.make_move(move)
        self.game_data.moves.append(move)
        if self.check_winner(move):
            self.game_data.winner = move.player
        self.current_player = PlayerEnum.WHITE if self.current_player == PlayerEnum.BLACK else PlayerEnum.BLACK
        return self.game_data.winner is not None

    def store_game(self):
        """Store the moves of the game as a JSON string."""
        return json.dumps(self.moves)

    def replay_game(self, game_json):
        """Reproduce the moves from a JSON string."""
        self.moves = json.loads(game_json)
        self.board = GomokuBoard()  # Reset the board
        self.winner = None  # Reset the winner

        for move in self.moves:
            player = move.player
            x = move.position_x
            y = move.position_y
            self.board[x][y] = player
            if self.check_winner(player, x, y):
                self.winner = player

    def display_board(self): ...

    def check_winner(self, last_move: Move) -> bool:
        """Check if the player has won the game after placing a stone at (x, y)."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        x = last_move.position_x
        y = last_move.position_y
        player = last_move.player

        def count_consecutive(d: tuple[int, int]):
            count = 1
            w_size, h_size = self.board.size
            dx, dy = d
            # Check in the positive direction
            for i in range(1, 5):
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < w_size and 0 <= ny < h_size and self.board[d] == player:
                    count += 1
                else:
                    break
            # Check in the negative direction
            for i in range(1, 5):
                nx, ny = x - i * dx, y - i * dy
                if 0 <= nx < w_size and 0 <= ny < h_size and self.board[d] == player:
                    count += 1
                else:
                    break
            return count

        for d in directions:
            if count_consecutive(d) >= 5:
                return True
        return False

    def initial_rule(self, rule_name):
        """Set the initial rule for the game (Swap or Swap2)."""
        if rule_name not in ["Swap", "Swap2"]:
            raise ValueError("Invalid rule name. Choose 'Swap' or 'Swap2'.")
        self.current_rule = rule_name
        self.rule_stage = 1  # Start the rule-specific move stages
        self.moves = []
        self.board = [[None for _ in range(15)] for _ in range(15)]  # Reset the board
        self.winner = None

    def apply_rule_move(self, player, x, y):
        """Apply a move according to the initial rule."""
        if self.current_rule is None:
            raise ValueError("No initial rule set. Use initial_rule() to set a rule.")

        if self.current_rule == "Swap":
            if self.rule_stage == 1:
                if self.make_move("X", x, y):
                    self.rule_stage += 1
            elif self.rule_stage == 2:
                if self.make_move("X", x, y):
                    self.rule_stage += 1
            elif self.rule_stage == 3:
                if self.make_move("O", x, y):
                    self.rule_stage = 4  # Swap rule completed
                    self.current_player = "O"  # Player 2 chooses their color
            else:
                return self.make_move(player, x, y)

        elif self.current_rule == "Swap2":
            if self.rule_stage == 1:
                if self.make_move("X", x, y):
                    self.rule_stage += 1
            elif self.rule_stage == 2:
                if self.make_move("X", x, y):
                    self.rule_stage += 1
            elif self.rule_stage == 3:
                if self.make_move("O", x, y):
                    self.rule_stage += 1
            elif self.rule_stage == 4:
                if self.make_move("O", x, y):
                    self.rule_stage = 5  # Swap2 rule completed
                    self.current_player = "X"  # Player 1 chooses their color
            else:
                return self.make_move(player, x, y)


if __name__ == "__main__":
    game = GomokuGame()
    print(game.board.display_board())
