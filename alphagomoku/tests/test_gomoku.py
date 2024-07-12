from game.gomoku import GomokuGame
from game.gomoku_utils import GridPosition, Move, PlayerEnum


def get_test_game():
    game = GomokuGame()
    initial_move = Move(PlayerEnum.BLACK, GridPosition(0, 0))
    game.reset()
    game.make_move(initial_move)
    return game, initial_move


def test_initialise_game():
    game, init_move = get_test_game()
    assert game.rule_stage == 0
    assert game.game_data.winner is None
    assert game.game_data.moves == [init_move]
    assert game.board.size == (15, 15)


def test_make_move_updates_game_data():
    game, move = get_test_game()
    assert game.game_data.moves == [move]
    assert game.game_data.winner is None
    assert game.current_player == PlayerEnum.WHITE


def test_can_store_gamedata_and_clone_boards():
    game, _ = get_test_game()
    game.store_game_data("test.json")
    game2 = GomokuGame.replay_game("test.json")
    assert game2.game_data.moves == game.game_data.moves
    assert game2.game_data.winner == game.game_data.winner
    assert game2.current_player == game.current_player


def check_winner():
    game, _ = get_test_game()
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(0, 1)))
    game.make_move(Move(PlayerEnum.BLACK, GridPosition(1, 0)))
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(0, 2)))
    game.make_move(Move(PlayerEnum.BLACK, GridPosition(2, 0)))
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(0, 3)))
    game.make_move(Move(PlayerEnum.BLACK, GridPosition(3, 0)))
    game.make_move(Move(PlayerEnum.WHITE, GridPosition(0, 4)))
    # The next move should win the game for black player with a vertical 5 in a row
    has_winner = game.make_move(Move(PlayerEnum.BLACK, GridPosition(4, 0)))
    assert (has_winner is True), "Game should have a winner for vertical win with black player"
    assert game.game_data.winner == PlayerEnum.BLACK, "Winner should be black player"
