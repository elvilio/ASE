from itertools import cycle
from typing import NamedTuple

class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="red"),
)


class Game:
    def __init__(self,
                 players=DEFAULT_PLAYERS,
                 board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._last_move_position = (-1, -1)
        self._winners_board = []
        self._tied_board = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size * self.board_size)]
            for row in range(self.board_size * self.board_size)
        ]
        self._winners_board = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._tied_board = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        """Return all possible winning combinations, i.e. rows, columns and diagonals."""
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._winners_board
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col

        right_big_cell = False
        offset = (int(row / self.board_size), int(col / self.board_size))


        if self._last_move_position == (-1,-1):
            right_big_cell = True
        elif (self._last_move_position == offset) and (self._winners_board[offset[0]][offset[1]].label == ""):
            right_big_cell = True
        elif self._winners_board[offset[0]][offset[1]].label != "":
            right_big_cell = False
        elif self._winners_board[self._last_move_position[0]][self._last_move_position[1]].label != "":
            right_big_cell = True
        elif self._tied_board[self._last_move_position[0]][self._last_move_position[1]].label != "":
            right_big_cell = True


        if self._current_moves[row][col].label != "":
            move_not_played = False
        else:
            move_not_played = True
        no_winner = not self.has_winner()

        return no_winner and move_not_played and right_big_cell

    def process_move(self, move):
        """Process the current move and check if it's a win."""
        row, col = move.row, move.col
        self._current_moves[row][col] = move

        offset = (int(row / self.board_size), int(col / self.board_size))
        self._last_move_position = (row % self.board_size, col % self.board_size)

        # first check for victory in small board
        for wc in self._winning_combos:
            wc = [
                (w[0] + offset[0] * self.board_size,
                 w[1] + offset[1] * self.board_size) for w in wc]

            if (row, col) in wc:
                flag = False
                for w in wc:
                    if self._current_moves[w[0]][w[1]].label != move.label:
                        flag = True
                if not flag:
                    self._winners_board[offset[0]][offset[1]] = Move(row, col, move.label)
                    for w in wc:
                        self.winner_combo.append(w)
        # second check victory in big board
        for wc in self._winning_combos:
            if offset in wc:
                flag = False
                for w in wc:
                    if self._winners_board[w[0]][w[1]].label != move.label:
                        flag = True
                if not flag:
                    self._has_winner = True
        # third check if tied
        flag = True
        for r in [e + offset[0] * self.board_size for e in range(self.board_size)]:
            for c in [e + offset[1] * self.board_size for e in range(self.board_size)]:
                if self._current_moves[r][c].label == "":
                    flag = False
        if flag:
            self._tied_board[offset[0]][offset[1]] = Move(offset[0], offset[1], "tied")

    def has_winner(self):
        """Return True if the game has a winner, and False otherwise."""
        return self._has_winner

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        # check whether a tie was reached.
        # There is no winner and all moves have been tried.
        if self.has_winner():
            return False
        for row, row_content in enumerate(self._winners_board):
            for col, col_content in enumerate(row_content):
                if col_content.label == "" and self._tied_board[row][col].label == "":
                    return False
        return True

    def toggle_player(self):
        """Return a toggled player."""
        # switches self.current_player to the other player.
        # Hint: https://docs.python.org/3/library/functions.html#next
        self.current_player = next(self._players)

    def reset_game(self):
        """Reset the game state to play again."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        for row, row_content in enumerate(self._winners_board):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        for row, row_content in enumerate(self._tied_board):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
