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
    last_move_player = PlayerEnum.BLACK
    current_player = PlayerEnum.WHITE

    # first move
    score = evaluator.evaluate_board(game.board, from_player=last_move_player, end_game=False)
    opp_score = evaluator.evaluate_board(game.board, from_player=current_player, end_game=False)
    print(score)
    print(game.board)
    print(evaluator.tabular_value_fn)
    assert score == 16, f"For a single move with double ended sides, the score should be 16 for {last_move_player}"
    assert opp_score == -16, f"For a single move with double ended sides, the score should be -16 for {current_player}"

    # make a second move
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(5, 5)))
    score = evaluator.evaluate_board(game.board, from_player=game.current_player, end_game=False)
    assert score == 0, "A symmetric position should cancel out, and the score should be 0"

    # make a third move, second for black
    game.make_move(Move(PlayerEnum.BLACK, GridPosition(5, 6)))
    score = evaluator.evaluate_board(game.board, from_player=game.current_player, end_game=False)
    print(score)
    print(game.board)
    print(evaluator.tabular_value_fn_opp)
    assert score == 16.0, "For a single move, the score should be 16.0"
