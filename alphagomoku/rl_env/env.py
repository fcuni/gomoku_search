import os
import sys
from enum import Enum
from typing import Any

import gymnasium as gym
import numpy as np
from evaluators.base_evaluator import BaseEvaluator
from game.gomoku import GomokuGame
from game.gomoku_ui import GomokuGameUI
from game.gomoku_utils import GridPosition, Move, StartingRule
from PyQt5.QtWidgets import QApplication

# Type hint for the step return type: [board observation, reward, done, terminated, debug_info]
StepReturnType = tuple[np.ndarray, float, bool, bool, dict]


class RenderMode(str, Enum):
    """Render mode for the environment."""
    CMD = "cmd"
    UI = "ui"


class GomokuEnv(gym.Env):
    """Gomoku environment for reinforcement learning."""
    def __init__(
        self,
        board_evaluator: BaseEvaluator,
        board_size: int | tuple[int, int] = 15,
        starting_rule: StartingRule = StartingRule.BASIC,
        save_board: bool = False,
        render_mode: RenderMode = RenderMode.CMD,
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
        self._render_mode = render_mode
        if render_mode == RenderMode.UI:
            os.environ["QT_QPA_PLATFORM"] = "wayland"
            self._app = QApplication(sys.argv)
            self._ui = GomokuGameUI(self.game)

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
        pos = GridPosition(action // self.game.board.size[0], action % self.game.board.size[1])
        return Move(self.game.current_player, pos)

    def step(self, action: int) -> StepReturnType:
        """Take a step in the environment."""
        assert self._is_reset, "Environment must be reset before taking a step"
        assert self.action_space.contains(action), f"Invalid action: {action}"
        assert self.game.game_data.winner is None, "Game is already done"

        self._is_done = self.game.make_move(self._make_move_from_action(action))
        reward = self.board_evaluator(game=self.game)
        self._steps += 1

        return self.game.board.to_numpy(), reward, self._is_done, self._is_terminated(), {}

    def render(self):
        """Render the environment."""
        if self._render_mode == RenderMode.CMD:
            self.game.display_board()
        elif self._render_mode == RenderMode.UI:
            # TODO: Fix the UI rendering through the environment
            self._ui.update_board()
            self._ui.show()
        else:
            raise ValueError(f"Invalid render mode: {self._render_mode}")
