from evaluators.base_evaluator import DummyEvaluator
from match.gomoku_match import GomokuMatch
from players.random_player import RandomPlayer
from rl_env.env import GomokuEnv, RenderMode

if __name__ == '__main__':
    env = GomokuEnv(board_evaluator=DummyEvaluator(), render_mode=RenderMode.CMD)
    player_one = RandomPlayer
    player_two = RandomPlayer
    match = GomokuMatch(player_one, player_two, env)

    match.play()
