import pytest
from game.gomoku_utils import GomokuBoard, Move, PlayerEnum


def test_initialise_board_and_make_move():
    board = GomokuBoard()
    # Default size is 15 by 15
    assert board.size == (15, 15)

    # Check positions are empty
    assert board[1, 1].get_player() is None, "Cell should be empty"
    assert board[5, 5].get_player() is None, "Cell should be empty"

    # Introduce a move and check cell
    move = Move(PlayerEnum.BLACK, 1, 1)
    board.make_move(move)
    assert board[(move.position_x, move.position_y)].get_player() == PlayerEnum.BLACK, "Cell should be black"
    assert board[5, 5].get_player() is None, "Cell should be empty"

    # Make an invalid move
    with pytest.raises(AssertionError):
        board.make_move(Move(PlayerEnum.WHITE, 20, 20))
