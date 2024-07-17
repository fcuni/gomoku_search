import numpy as np
from evaluators.base_evaluator import MAX_END_GAME_SCORE, BaseEvaluator
from game.gomoku_utils import GomokuBoard, GridPosition, PlayerEnum


class HeuristicEvaluator(BaseEvaluator):
    """
    Heuristic evaluator for the board.

    This evaluator uses a simple heuristic to evaluate the board. It assigns a score to the board based on the
    structures available to each player.

    A structure is a group of cells that are occupied by the same player and are connected in a certain way. The
    structures can be open, close or semi-open, and the score attaches a multiplier to each of these.

    The score of each structure is its length times a weight. The final score is the sum of the scores of all the
    structures for the player minus the sum of the scores of the structures for the opponent.
    """
    def __init__(self):
        super().__init__()
        self.tabular_value_fn: np.ndarray | None = None
        self.tabular_value_fn_opp: np.ndarray | None = None
        # Align scores with the number of cells in a row
        self._scores = np.array([0, 1, 3, 9, 27, 1000])

    def evaluate_board(self, board: GomokuBoard, from_player: PlayerEnum, end_game: bool) -> int:
        """Evaluate the board and return a score."""
        if end_game:
            return self._evaluate_end_game(board)
        return self._evaluate_board(board, from_player)

    def _evaluate_end_game(self, board: GomokuBoard) -> int:
        """Evaluate the board at the end of the game."""
        return MAX_END_GAME_SCORE

    def _evaluate_board(self, board: GomokuBoard, from_player: PlayerEnum) -> int:
        """Evaluate the board in the middle of the game."""
        self.tabular_value_fn = np.zeros((board.size), dtype=int)
        seen_positions: list[bool] = [False] * np.prod(board.size)
        x, y = board.size
        for i in range(x):
            for j in range(y):
                position = x * i + j
                if not seen_positions[position]:
                    chain_value = self._get_cell_value(board, i, j, seen_positions, from_player)
                    self.tabular_value_fn[i, j] = chain_value
        return self.tabular_value_fn.sum()

    def _get_cell_value(
        self, board: GomokuBoard, x: int, y: int, seen_positions: list[bool], from_player: PlayerEnum
    ) -> int:
        """Get the characteristics of a chain."""
        cell_values: list[int] = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                seen_positions[x * dx + dy] = True
                cell_values.append(self._get_value_helper_fn(board, x, y, dx, dy, seen_positions, from_player))
        return max(cell_values)

    def _is_valid_position(self, board: GomokuBoard, x: int, y: int) -> bool:
        """Check if a position is valid."""
        return 0 <= x < board.size[0] and 0 <= y < board.size[1]

    def _get_value_helper_fn(
        self, board: GomokuBoard, x: int, y: int, dx: int, dy: int, seen_positions: list[bool], from_player: PlayerEnum
    ) -> int:
        """Get the value of a chain."""
        length = 0
        current_player = None
        ends = [False, False]
        if self._is_valid_position(board, x - dx, y - dy):
            ends[0] = board[GridPosition(x - dx, y - dy)].get_player() is None
        while True:
            x += dx
            y += dy
            if not self._is_valid_position(board, x, y):
                break
            current_player = board[GridPosition(x, y)].get_player()
            if current_player is None:
                ends[1] = True
                break
            if board[GridPosition(x, y)].get_player() != current_player:
                break
            length += 1
            seen_positions[x * dx + y * dy] = True
        chain_end_multiplier = sum(ends)
        chain_player_multiplier = 1 if from_player == current_player else -1
        chain_multiplier = chain_end_multiplier * chain_player_multiplier

        return chain_multiplier * self._scores[length]


if __name__ == "__main__":
    from tests.test_evaluators import dummy_game
    game = dummy_game()
    evaluator = HeuristicEvaluator()
    last_move_player = PlayerEnum.BLACK
    current_player = PlayerEnum.WHITE

    # first move
    score = evaluator.evaluate_board(game.board, from_player=last_move_player, end_game=False)
    opp_score = evaluator.evaluate_board(game.board, from_player=current_player, end_game=False)
    print(score)
    print(game.board)
    print(evaluator.tabular_value_fn)
    assert score == 16, f"For a single move with double ended sides, the score should be 16 for {last_move_player}"
    assert opp_score == -16, f"For a single move with double ended sides, the score should be -16 for {current_player}"
