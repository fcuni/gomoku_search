import numpy as np
from evaluators.base_evaluator import MAX_END_GAME_SCORE, BaseEvaluator
from game.gomoku_utils import GomokuBoard, GridPosition, Move, PlayerEnum


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
        self.score_weights = np.array([0, 1, 3, 9, 27, 1000])

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
        x, y = board.size
        for i in range(x):
            for j in range(y):
                cell_owner = board[GridPosition(i, j)].get_player()
                if cell_owner is not None:
                    chain_value = 0
                else:
                    chain_value = self._get_cell_value(board, i, j, from_player)
                self.tabular_value_fn[i, j] = chain_value
        return self.tabular_value_fn.sum()

    def _get_cell_value(self, board: GomokuBoard, x: int, y: int, from_player: PlayerEnum) -> int:
        """Get the characteristics of a chain."""
        cell_values: list[tuple[int, PlayerEnum | None]] = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                cell_values += [self._get_value_helper_fn(board, x, y, dx, dy)]
        max_value, played_by = max(cell_values, key=lambda x: x[0])
        player_multiplier = 1 if played_by == from_player else -1
        return player_multiplier * max_value

    def _is_valid_position(self, board: GomokuBoard, x: int, y: int) -> bool:
        """Check if a position is valid."""
        return 0 <= x < board.size[0] and 0 <= y < board.size[1]

    def _get_value_helper_fn(self, board: GomokuBoard, x: int, y: int, dx: int,
                             dy: int) -> tuple[int, PlayerEnum | None]:
        """Get the value of a chain."""
        length = 0
        chain_owner = None
        ends = [False, False]
        if self._is_valid_position(board, x - dx, y - dy):
            # check if the cell prior to the chain is empty
            ends[0] = board[GridPosition(x - dx, y - dy)].get_player() is None
        while True:
            x += dx
            y += dy
            if not self._is_valid_position(board, x, y):
                # if going outside of the bounds of the board just break
                break
            # assign player that owns the cell, if any
            current_player = board[GridPosition(x, y)].get_player()
            if current_player is None:
                # if no one owns the cell, the chain is broken and open-ended, break
                ends[1] = True
                break
            if chain_owner is None:
                # if the chain has no owner, assign the owner
                chain_owner = current_player
            if chain_owner != current_player:
                # if the cell is owned by the opponent, the chain is broken and closed-ended, break
                break
            # otherwise, it is owned by the current player, increase the length of the chain by 1
            length += 1
        # assign multiplier to the chain based on: open, semi-open, closed as (2, 1, 0)
        chain_end_multiplier = sum(ends)

        return chain_end_multiplier * self.score_weights[length], chain_owner
