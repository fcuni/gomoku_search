from players.base_player import BasePlayer
from rl_env.env import GomokuEnv, RenderMode


class HumanPlayer(BasePlayer):
    """A human controlled player that can play moves in the game."""
    def __init__(self, env: GomokuEnv):
        super().__init__(env)

    def play_turn(self) -> bool:
        """If the render mode is UI, wait for the user to make a move. Else, ask for an input from the CMD."""
        if self.env._render_mode == RenderMode.UI:
            done = self.env._ui.wait_for_human_move()
        else:
            user_input = input("Enter the move to play with coords (row, column): ")
            row, col = user_input.split(",")
            action = int(row) * self.env.game.board.size[0] + int(col)
            _, _, done, _, _ = self.env.step(action)
        return done
