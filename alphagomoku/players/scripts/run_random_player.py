from evaluators.base_evaluator import DummyEvaluator
from players.random_player import RandomPlayer
from rl_env.env import GomokuEnv, RenderMode

if __name__ == '__main__':
    env = GomokuEnv(board_evaluator=DummyEvaluator(), render_mode=RenderMode.CMD)
    player = RandomPlayer(env)

    player.play()
