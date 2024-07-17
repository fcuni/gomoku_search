from evaluators.base_evaluator import DummyEvaluator
from rl_env.env import GomokuEnv

if __name__ == '__main__':
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    env.reset()
    max_steps = 100

    while env._steps < max_steps:
        action = int(input("Enter action: "))
        obs, reward, done, _, _ = env.step(action)
        env.render()
        if done:
            print(f"Game is done and {env.game.game_data.winner} has won!")
            break
