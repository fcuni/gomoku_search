import os
import sys
from collections.abc import Callable

from game.gomoku_ui import GomokuGameUI, RenderMode
from game.gomoku_utils import PlayerEnum
from players.base_player import BasePlayer
from PyQt5.QtWidgets import QApplication
from rl_env.env import GomokuEnv

PlayerFn = Callable[[GomokuEnv], BasePlayer]


class GomokuMatch:
    """A class to run a match between two players in the Gomoku game."""
    def __init__(
        self,
        player_black_fn: PlayerFn,
        player_white_fn: PlayerFn,
        env: GomokuEnv,
        use_ui: bool = False,
    ):
        self.env = env
        self.player_black = player_black_fn(env)
        self.player_white = player_white_fn(env)
        self._render_mode = RenderMode.UI if use_ui else RenderMode.CMD

        # setup ui if render mode is UI
        if use_ui:
            os.environ["QT_QPA_PLATFORM"] = "wayland" if sys.platform == "linux" else "xlge"
            self._app = QApplication(sys.argv)
            self._ui = GomokuGameUI(self.env.game)

    def play(self):
        """Play a match between the two players."""
        self.env.reset()
        done = False
        while not done:
            if self.env.game.current_player == PlayerEnum.BLACK:
                done = self.player_black.play_turn()
            else:
                done = self.player_white.play_turn()
            if self._render_mode == RenderMode.UI:
                # TODO: fix UI rendering
                self._ui.update_board()
            else:
                self.env.render()
            if done:
                print(f"The winner is of the game is {self.env.game.game_data.winner}")


if __name__ == "__main__":
    from evaluators.base_evaluator import DummyEvaluator
    from players.random_player import RandomPlayer

    evaluator = DummyEvaluator()
    env = GomokuEnv(board_evaluator=evaluator, save_board=True)
    match = GomokuMatch(RandomPlayer, RandomPlayer, env, use_ui=True)
    match.play()
