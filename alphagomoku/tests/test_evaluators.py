import numpy as np
from evaluators.base_evaluator import MAX_END_GAME_SCORE, BaseEvaluator
from evaluators.heuristic_evaluator import HeuristicEvaluator
from game.gomoku import GomokuGame
from game.gomoku_utils import GridPosition, Move, PlayerEnum


def dummy_game() -> GomokuGame:
    """Create a dummy game."""
    game = GomokuGame()
    dummy_move = Move(PlayerEnum.BLACK, GridPosition(0, 0))

    game.reset()
    game.make_move(dummy_move)
    return game


def test_evaluate_endgame():
    """Test the evaluate_board method at the end of the game."""
    game = dummy_game()

    # Default evaluator returns the size of the board
    base_evaluator = BaseEvaluator()
    score = base_evaluator.evaluate_board(game.board, from_player=game.current_player, end_game=True)
    assert score == np.prod(game.board.size), f"Endgame score is not the size of the board {np.prod(game.board.size)}"
    # Heuristic evaluator returns the size of the board
    evaluator = HeuristicEvaluator()
    score = evaluator.evaluate_board(game.board, from_player=game.current_player, end_game=True)
    assert score == MAX_END_GAME_SCORE, f"Endgame is not {MAX_END_GAME_SCORE=}"


def test_heuristic_evaluate_board():
    """Test the evaluate_board method with a single move."""
    game = dummy_game()
    evaluator = HeuristicEvaluator()
    score_weights = evaluator.score_weights
    first_player = PlayerEnum.BLACK
    second_player = PlayerEnum.WHITE

    # first move
    score = evaluator.evaluate_board(game.board, from_player=first_player, end_game=False)
    expected_score = 3 * score_weights[1]
    assert score == expected_score, f"For a single move, the score should be {expected_score} for {first_player}"

    # opponents score should be the negative of the current player's score
    opp_score = evaluator.evaluate_board(game.board, from_player=second_player, end_game=False)
    assert opp_score == -score, f"For the opponent, the score should be -{expected_score} for {second_player}"

    # second move, balanced position
    move = Move(PlayerEnum.WHITE, GridPosition(14, 14))
    game.make_move(move)
    score = evaluator.evaluate_board(game.board, from_player=second_player, end_game=False)
    opp_score = evaluator.evaluate_board(game.board, from_player=first_player, end_game=False)
    assert score == 0, f"For a balanced position, the score should be 0 for {first_player}"
    assert opp_score == 0, f"For a balanced position, the score should be 0 for {second_player}"

    # third move, chain of length 2 for BLACK
    move = Move(PlayerEnum.BLACK, GridPosition(0, 1))
    game.make_move(move)
    score = evaluator.evaluate_board(game.board, from_player=first_player, end_game=False)
    expected_score = score_weights[2] + score_weights[1]
    assert score == evaluator.score_weights[2], f"For a chain of length 2, the score should be {expected_score} for {first_player}"

    # fourth move, central move for WHITE
    move = Move(PlayerEnum.WHITE, GridPosition(7, 7))
    game.make_move(move)
    score = evaluator.evaluate_board(game.board, from_player=second_player, end_game=False)
    print(game.board)
    print(evaluator.tabular_value_fn)
    expected_score = 8 * 2 * score_weights[1] - score_weights[2]
    assert score == expected_score, f"After the central move, the score should be {expected_score} for {second_player}"
