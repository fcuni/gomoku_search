from typing import Any

import gymnasium as gym
import numpy as np
from evaluators.base_evaluator import BaseEvaluator
from evaluators.heuristic_evaluator import HeuristicEvaluator
from game.gomoku import GomokuGame
from game.gomoku_utils import GridPosition, Move, StartingRule

# Type hint for the step return type: [board observation, reward, done, terminated, debug_info]
StepReturnType = tuple[np.ndarray, float, bool, bool, dict]


class GomokuEnv(gym.Env):
    """Gomoku environment for reinforcement learning."""
    def __init__(
        self,
        board_evaluator: BaseEvaluator = HeuristicEvaluator(),
        board_size: int | tuple[int, int] = 15,
        starting_rule: StartingRule = StartingRule.BASIC,
        save_board: bool = False,
    ):
        """Initialise the environment."""
        self.game: GomokuGame = GomokuGame(starting_rule=starting_rule, board_size=board_size)
        self.action_space: gym.Space = gym.spaces.Discrete(np.prod(self.game.board.size))
        self.observation_space: gym.Space = gym.spaces.Box(low=0, high=2, shape=self.game.board.size, dtype=np.int8)

        self.board_evaluator = board_evaluator
        self._is_reset = False
        self._is_done = False
        self._save_board = save_board
        self._steps = 0

    @property
    def is_done(self) -> bool:
        """Return whether the game is done."""
        return self._is_done

    @property
    def is_terminated(self) -> bool:
        """Return whether the game is terminated."""
        return self._is_terminated()

    def get_valid_actions(self) -> np.ndarray:
        """Get the valid actions."""
        action_mask = self.game.get_available_positions_mask()
        return np.where(action_mask.flatten() == 1)[0]

    def reset(self) -> tuple[np.ndarray, dict[str, Any]]:    # type: ignore
        """Reset the environment."""
        self._is_reset = True
        self.game.reset()
        self._steps = 0

        return self.game.board.to_numpy(), {}

    def _is_terminated(self) -> bool:
        """Terminate the game and return True if the game is done. For now, we do not have a termination condition."""
        return self._is_done

    def _make_move_from_action(self, action: int) -> Move:
        """Make a move from the action."""
        pos = GridPosition.from_int(action, board_size=self.game.board.size)
        return Move(self.game.current_player, pos)

    def step(self, action: int) -> StepReturnType:
        """Take a step in the environment."""
        assert self._is_reset, "Environment must be reset before taking a step"
        assert self.action_space.contains(action), f"Invalid action: {action}"
        assert self.game.game_data.winner is None, f"Game is already done after {self._steps} steps."

        self._is_done = self.game.make_move(self._make_move_from_action(action))
        reward = self.board_evaluator(game=self.game)
        self._steps += 1

        if self._save_board and self._is_done:
            self.game.board.store_board()
            self.game.store_game_data()

        return self.game.board.to_numpy(), reward, self._is_done, self._is_terminated(), {}

    def render(self):
        """Render the environment."""
        self.game.display_board()
