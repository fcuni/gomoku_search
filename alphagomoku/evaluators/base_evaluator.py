from abc import abstractmethod

from game.gomoku_utils import GomokuBoard


class BaseEvaluator:
    """Base class for the board evaluator."""
    @abstractmethod
    def evaluate_board(self, board: GomokuBoard, end_game: bool) -> float:
        """Evaluate the board and return a score."""
        raise NotImplementedError()


class DummyEvaluator(BaseEvaluator):
    """Dummy evaluator for testing."""
    def evaluate_board(self, board: GomokuBoard, end_game: bool) -> float:
        """Evaluate the board and return a score."""
        return 0.0
