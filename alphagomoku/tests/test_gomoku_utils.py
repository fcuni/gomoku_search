import pytest
from game.gomoku_utils import GomokuBoard, GridPosition, Move, PlayerEnum


def test_initialise_board_and_make_move():
    board = GomokuBoard()
    # Default size is 15 by 15
    assert board.size == (15, 15)

    empty_position = GridPosition(5, 5)
    assert board[empty_position].get_player() is None, "Cell should be empty"

    # Introduce a move and check cell
    move = Move(PlayerEnum.BLACK, GridPosition(1, 1))
    board.make_move(move)
    assert board[(move.position)].get_player() == PlayerEnum.BLACK, "Cell should be black"
    assert board[empty_position].get_player() is None, "Cell should be empty"

    # Make an invalid move
    with pytest.raises(AssertionError):
        impossible_position = GridPosition(20, 20)
        board.make_move(Move(PlayerEnum.WHITE, impossible_position))
