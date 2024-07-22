from abc import abstractmethod

from rl_env.env import GomokuEnv


class BasePlayer:
    """Base class for a player in the game."""
    def __init__(self, env: GomokuEnv):
        self.env = env

    @abstractmethod
    def play_turn(self) -> bool:
        raise NotImplementedError
