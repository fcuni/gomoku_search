import numpy as np
from players.base_player import BasePlayer
from rl_env.env import GomokuEnv


def select_random_action(valid_actions: np.ndarray):
    """Select a random action, given that all actions are assumed to have uniform probability."""
    return np.random.choice(valid_actions)


class RandomPlayer(BasePlayer):
    """A player that plays random moves in the game. Mostly used for testing purposes."""
    def __init__(self, env: GomokuEnv):
        super().__init__(env)

    def get_action(self) -> int:
        """Get a random valid action to play."""
        valid_actions = self.env.get_valid_actions()
        if valid_actions.size > 0:
            return select_random_action(valid_actions)
        raise ValueError("No valid actions to play.")

    def play_turn(self) -> bool:
        """Play a turn in the game."""
        action = self.get_action()
        _, _, done, _, _ = self.env.step(action)
        return done
