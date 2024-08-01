from evaluators.base_evaluator import BaseEvaluator
from game.gomoku_utils import GomokuBoard, PlayerEnum


class SparseEvaluator(BaseEvaluator):
    """
    Sparse evaluator for the board.

    This class only returns a score of 1 at the end of the game. Otherwise, it returns 0.
    """
    def evaluate_board(self, board: GomokuBoard, from_player: PlayerEnum, end_game: bool) -> int:
        if end_game:
            return 1
        # in case of a draw, return 0
        return 0
