from collections.abc import Callable

from game.gomoku_utils import PlayerEnum
from players.base_player import BasePlayer
from rl_env.env import GomokuEnv

PlayerFn = Callable[[GomokuEnv], BasePlayer]


class GomokuMatch:
    """A class to run a match between two players in the Gomoku game."""
    def __init__(self, player_black_fn: PlayerFn, player_white_fn: PlayerFn, env: GomokuEnv):
        self.env = env
        self.player_black = player_black_fn(env)
        self.player_white = player_white_fn(env)

    def play(self):
        """Play a match between the two players."""
        self.env.reset()
        done = False
        while not done:
            if self.env.game.current_player == PlayerEnum.BLACK:
                done = self.player_black.play_turn()
            else:
                done = self.player_white.play_turn()
            self.env.render()
            if done:
                print(f"The winner is of the game is {self.env.game.game_data.winner}")
