import pytest
from evaluators.base_evaluator import DummyEvaluator
from game.gomoku_utils import PlayerEnum
from rl_env.env import GomokuEnv


def test_env_initialise():
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    assert env.game.board.size == (15, 15), "Default board size should be 15x15"
    assert env.action_space.n == 225, "Action space should be 225"
    assert env.observation_space.shape == (15, 15), "Observation space should be (15, 15)"
    assert env._is_reset is False, "Environment should not be reset"


def test_env_reset():
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    # Make a move before resetting, which should raise an error
    with pytest.raises(AssertionError):
        env.step(0)

    # reset the environment
    env.reset()
    assert env._is_reset is True, "Environment should be reset"
    assert env._steps == 0, "No steps should have been taken"


def test_env_take_step():
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    env.reset()
    obs, reward, done, _, _ = env.step(0)

    assert obs.shape == (15, 15), "Observation shape should be (15, 15)"
    assert reward == 0.0, "Reward should be 0"
    assert done is False, "Game should not be done"
    assert env._steps == 1, "One step should have been taken"
    assert env.game.current_player == PlayerEnum.WHITE, "Player should have changed"


def test_env_invalid_action():
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    env.reset()
    # Make an invalid move
    with pytest.raises(AssertionError):
        env.step(225)
    # Make a valid move
    env.step(0)
    # Make another invalid move
    with pytest.raises(AssertionError):
        env.step(0)
    # Make a valid move
    env.step(1)


def test_env_game_done():
    env = GomokuEnv(board_evaluator=DummyEvaluator())
    env.reset()
    # Make a move to win the game
    for i in range(9):
        if i % 2 == 0:
            env.step(i // 2)
        else:
            env.step(i + 100)
    assert env.game.game_data.winner == PlayerEnum.BLACK, "Game should be done, and black should have won"
    # Try to make another move
    with pytest.raises(AssertionError):
        env.step(5)
    # Reset the environment
    env.reset()
    assert env.game.game_data.winner is None, "Game should not be done"
    assert env._is_reset is True, "Environment should be reset"
    assert env._steps == 0, "No steps should have been taken"
    assert env.game.current_player == PlayerEnum.BLACK, "Player should be black"
