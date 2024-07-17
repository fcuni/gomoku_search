from abc import abstractmethod

import numpy as np
from game.gomoku import GomokuGame
from game.gomoku_utils import GomokuBoard, PlayerEnum

MAX_END_GAME_SCORE = 1_000_000


class BaseEvaluator:
    """Base class for the board evaluator."""
    def __call__(self, game: GomokuGame) -> int:
        """Evaluate the board and return a score."""
        return self.evaluate_board(game.board, game.current_player, game.game_data.winner is not None)

    @abstractmethod
    def evaluate_board(self, board: GomokuBoard, from_player: PlayerEnum, end_game: bool) -> int:
        """Evaluate the board and return a score."""
        if end_game:
            return self._evaluate_end_game(board)
        raise NotImplementedError()

    def _evaluate_end_game(self, board: GomokuBoard) -> int:
        """Evaluate the board at the end of the game. By default, return the size of the board."""
        return np.prod(board.size, dtype=int)


class DummyEvaluator(BaseEvaluator):
    """Dummy evaluator for testing."""
    def evaluate_board(self, board: GomokuBoard, from_player: PlayerEnum, end_game: bool) -> int:
        """Evaluate the board and return a score."""
        return 0

    def _evaluate_end_game(self, board: GomokuBoard) -> int:
        """Evaluate the board at the end of the game."""
        return 0
