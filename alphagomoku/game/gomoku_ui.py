import os
import sys
from dataclasses import dataclass
from enum import Enum

from game.gomoku import GomokuGame
from game.gomoku_utils import GridPosition, Move, PlayerEnum

# PyQT5 is used for the UI
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QWidget,
)


class RenderMode(str, Enum):
    """Render mode for the environment."""
    CMD = "cmd"
    UI = "ui"


@dataclass
class UIConfig:
    cell_size: int = 30
    stone_radius: int = 12


class GomokuGameUI(QWidget):
    def __init__(self, game: GomokuGame, ui_config: UIConfig = UIConfig()):
        super().__init__()
        self._game = game
        self._board_size = game.board.size
        self.config = ui_config
        self._last_move_ix: int | None = None

        self._init_ui()
        self._draw_board()

    def _init_ui(self):
        self.setWindowTitle("Gomoku Game")
        self.setFixedSize((self._board_size[0] + 1) * self.config.cell_size,
                          (self._board_size[1] + 1) * self.config.cell_size)

        self.canvas = QGraphicsView()
        self.scene = QGraphicsScene()
        self.canvas.setScene(self.scene)

        self.canvas_board = QGridLayout()
        self.setLayout(self.canvas_board)

        # Create labels for rows and columns
        for i in range(self._board_size[0]):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)    # type: ignore
            self.canvas_board.addWidget(label, 0, i + 1)
        for i in range(self._board_size[1]):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)    # type: ignore
            self.canvas_board.addWidget(label, i + 1, 0)

        self.canvas_board.addWidget(self.canvas, 1, 1, self._board_size[0], self._board_size[1])

        self.canvas_board.setContentsMargins(0, 0, 0, 0)

    def _draw_board(self):
        cell_size = self.config.cell_size
        width, height = self._board_size
        pen = QPen(Qt.black, 2, Qt.SolidLine)    # type: ignore

        self.scene.addRect(0, 0, width * cell_size, height * cell_size, pen)

        for i in range(width):
            self.scene.addLine(i * cell_size, 0, i * cell_size, height * cell_size, Qt.black)    # type: ignore
            for j in range(height):
                self.scene.addLine(0, j * cell_size, width * cell_size, j * cell_size, Qt.black)    # type: ignore

        if self._game.turn != 0:
            for move in self._game.game_data.moves:
                self.draw_stone(move.position, move.player)
            if self._game.game_data.winner is not None:
                self.setDisabled(True)

        self._last_move_ix = self._game.turn

    def update_board(self):
        for move in self._game.game_data.moves[self._last_move_ix:]:
            self.draw_stone(move.position, move.player)
        self._last_move_ix = self._game.turn

    def draw_stone(self, position: GridPosition, player: PlayerEnum):
        row, col = position()
        cell_size = self.config.cell_size
        stone_radius = self.config.stone_radius

        x = col * cell_size + cell_size // 2 - stone_radius
        y = row * cell_size + cell_size // 2 - stone_radius

        color = Qt.black if player == PlayerEnum.BLACK else Qt.white    # type: ignore
        outline = Qt.white if player == PlayerEnum.BLACK else Qt.black    # type: ignore

        stone = QGraphicsEllipseItem(x, y, stone_radius * 2, stone_radius * 2)
        stone.setBrush(color)
        stone.setPen(outline)
        self.scene.addItem(stone)

    def mousePressEvent(self, event):    # type: ignore
        if event.button() == Qt.LeftButton:    # type: ignore
            y = event.x() // self.config.cell_size - 1
            x = event.y() // self.config.cell_size - 1
            current_player = self._game.current_player
            move = Move(current_player, GridPosition(x, y))
            try:
                is_winning = self._game.make_move(move)
                self.draw_stone(move.position, current_player)
                print(move)
                if is_winning:
                    print(f"Player {current_player.value} wins!")
                    # freeze the application
                    self.setDisabled(True)
            except AssertionError:
                print(f"Invalid move: {move}")


def show_board_in_ui(game: GomokuGame | None = None, gamedata_file: str | None = None):
    """Show the board in a UI."""
    assert game or gamedata_file, "Either the environment or the game data file must be provided."
    if gamedata_file:
        full_path = os.path.join(os.getcwd(), gamedata_file)
        game = GomokuGame.replay_game(full_path, print_board=False)

    os.environ["QT_QPA_PLATFORM"] = "wayland" if sys.platform == "linux" else "xlge"

    app = QApplication(sys.argv)
    ui = GomokuGameUI(game)    # type: ignore
    ui.show()
    sys.exit(app.exec_())
