from evaluators.base_evaluator import BaseEvaluator
from game.gomoku_utils import GomokuBoard


class SparseEvaluator(BaseEvaluator):
    """
    Sparse evaluator for the board.

    This class only returns a score of 1 at the end of the game. Otherwise, it returns 0.

    """
    def evaluate_board(self, board: GomokuBoard, end_game: bool) -> int:
        if end_game:
            return self._evaluate_end_game(board)
        return 0

    def _evaluate_end_game(self, board: GomokuBoard) -> int:
        return 1
