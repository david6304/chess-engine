# game.py
from board import Board

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.game_over = False
        self.winner = None

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def make_move(self, start, end):
        piece = self.board.get_piece(start)
        if piece is None or piece.color != self.current_turn:
            return False
        if self.board.move_piece(start, end):
            # Check for checkmate on the opponent's side
            opponent = 'black' if self.current_turn == 'white' else 'white'
            if self.board.is_checkmate(opponent):
                self.game_over = True
                self.winner = self.current_turn
            else:
                self.switch_turn()
            return True
        return False

    def get_legal_moves(self, pos):
        return self.board.get_legal_moves_for_piece(pos)
