import numpy as np
import pytest
from game.gomoku_utils import GomokuBoard, GomokuCell, GridPosition, Move, PlayerEnum


def test_grid_position():
    position = GridPosition(5, 5)
    assert position.x == 5
    assert position.y == 5
    assert position() == (5, 5)


def test_initialise_cell():
    cell = GomokuCell()
    # Originally the cell should be empty (no player)
    assert cell.get_player() is None, "Cell should be empty"
    # Set the player to black and check if it is black
    cell.set_player(PlayerEnum.BLACK)
    assert cell.get_player() == PlayerEnum.BLACK, "Cell should be black"
    # Try to set the player to white, which should raise an error
    with pytest.raises(AssertionError):
        cell.set_player(PlayerEnum.WHITE)


def test_initialise_board_and_make_move():
    board = GomokuBoard()
    # Default size is 15 by 15
    assert board.size == (15, 15)

    empty_position = GridPosition(5, 5)
    assert board[empty_position].get_player() is None, "Cell should be empty"

    # Introduce a move and check cell
    move = Move(PlayerEnum.BLACK, GridPosition(1, 1))
    board.make_move(move)
    assert board[move.position].get_player() == PlayerEnum.BLACK, "Cell should be black"
    assert board[empty_position].get_player() is None, "Cell should be empty"

    # Make an invalid move
    with pytest.raises(AssertionError):
        impossible_position = GridPosition(20, 20)
        board.make_move(Move(PlayerEnum.WHITE, impossible_position))


def test_available_positions():
    dummy_move = Move(PlayerEnum.BLACK, GridPosition(5, 5))
    board = GomokuBoard()
    nx, ny = board.size
    all_positions = [GridPosition(x, y) for x in range(nx) for y in range(ny)]

    # Initially all positions should be available
    assert board.available_positions == all_positions
    assert board.get_available_positions_mask().all()

    board.make_move(dummy_move)
    # After a move, the position should be removed from the available positions
    # and the mask should be updated
    assert dummy_move.position not in board.available_positions, "Position should be removed"

    # Test the mask
    position_mask = board.get_available_positions_mask()
    assert position_mask[5 * nx + 5] == -1, "Position should be masked"
    position_mask = np.delete(position_mask, 5 * nx + 5)
    assert position_mask.all(), "All other positions should be available"
