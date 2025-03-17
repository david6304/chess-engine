# board.py
import copy

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type  # 'P', 'R', 'N', 'B', 'Q', 'K'
        self.color = color      # 'white' or 'black'
        self.has_moved = False

    def __repr__(self):
        return f"{self.color[0].upper()}{self.type}"

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None  # to track moves for en passant
        self.initialize_board()

    def initialize_board(self):
        # Pawns
        for i in range(8):
            self.board[6][i] = Piece('P', 'white')
            self.board[1][i] = Piece('P', 'black')
        # Rooks
        self.board[7][0] = Piece('R', 'white')
        self.board[7][7] = Piece('R', 'white')
        self.board[0][0] = Piece('R', 'black')
        self.board[0][7] = Piece('R', 'black')
        # Knights
        self.board[7][1] = Piece('N', 'white')
        self.board[7][6] = Piece('N', 'white')
        self.board[0][1] = Piece('N', 'black')
        self.board[0][6] = Piece('N', 'black')
        # Bishops
        self.board[7][2] = Piece('B', 'white')
        self.board[7][5] = Piece('B', 'white')
        self.board[0][2] = Piece('B', 'black')
        self.board[0][5] = Piece('B', 'black')
        # Queens
        self.board[7][3] = Piece('Q', 'white')
        self.board[0][3] = Piece('Q', 'black')
        # Kings
        self.board[7][4] = Piece('K', 'white')
        self.board[0][4] = Piece('K', 'black')

    def in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, pos):
        row, col = pos
        if self.in_bounds(row, col):
            return self.board[row][col]
        return None

    def move_piece(self, start, end):
        """
        Move piece from start to end if the move is legal.
        Return True if the move is successful.
        """
        legal_moves = self.get_legal_moves_for_piece(start)
        if end in legal_moves:
            piece = self.get_piece(start)
            target = self.get_piece(end)
            # Handle castling
            if piece.type == 'K' and abs(end[1] - start[1]) == 2:
                self.perform_castling(start, end)
            # Handle en passant
            elif piece.type == 'P' and start[1] != end[1] and target is None:
                self.perform_en_passant(start, end)
            else:
                self.board[end[0]][end[1]] = piece
                self.board[start[0]][start[1]] = None
                piece.has_moved = True
                # Auto-promote pawn to queen upon reaching the back rank
                if piece.type == 'P' and (end[0] == 0 or end[0] == 7):
                    piece.type = 'Q'
            self.last_move = (start, end, piece)
            return True
        return False

    def perform_castling(self, start, end):
        king = self.get_piece(start)
        self.board[end[0]][end[1]] = king
        self.board[start[0]][start[1]] = None
        king.has_moved = True
        # Move the rook accordingly
        if end[1] == 6:  # kingside
            rook_start = (start[0], 7)
            rook_end = (start[0], 5)
        else:  # queenside (end[1] == 2)
            rook_start = (start[0], 0)
            rook_end = (start[0], 3)
        rook = self.get_piece(rook_start)
        self.board[rook_end[0]][rook_end[1]] = rook
        self.board[rook_start[0]][rook_start[1]] = None
        rook.has_moved = True

    def perform_en_passant(self, start, end):
        piece = self.get_piece(start)
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None
        piece.has_moved = True
        # Remove the captured pawn
        if piece.color == 'white':
            captured_pos = (end[0] + 1, end[1])
        else:
            captured_pos = (end[0] - 1, end[1])
        self.board[captured_pos[0]][captured_pos[1]] = None

    def get_legal_moves_for_piece(self, pos):
        """
        Returns a list of legal destination positions for the piece at pos.
        """
        piece = self.get_piece(pos)
        if piece is None:
            return []
        if piece.type == 'P':
            moves = self.get_pawn_moves(pos, piece)
        elif piece.type == 'N':
            moves = self.get_knight_moves(pos, piece)
        elif piece.type == 'B':
            moves = self.get_sliding_moves(pos, piece, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif piece.type == 'R':
            moves = self.get_sliding_moves(pos, piece, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece.type == 'Q':
            moves = self.get_sliding_moves(pos, piece, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece.type == 'K':
            moves = self.get_king_moves(pos, piece)
        else:
            moves = []
        # Filter out moves that leave the king in check
        legal_moves = []
        for move in moves:
            if self.move_doesnt_cause_check(pos, move):
                legal_moves.append(move)
        return legal_moves

    def move_doesnt_cause_check(self, start, end):
        temp_board = copy.deepcopy(self)
        piece = temp_board.get_piece(start)
        # Handle special moves in simulation
        if piece.type == 'K' and abs(end[1] - start[1]) == 2:
            temp_board.perform_castling(start, end)
        elif piece.type == 'P' and start[1] != end[1] and temp_board.get_piece(end) is None:
            temp_board.perform_en_passant(start, end)
        else:
            temp_board.board[end[0]][end[1]] = piece
            temp_board.board[start[0]][start[1]] = None
            piece.has_moved = True
        return not temp_board.is_in_check(piece.color)

    def get_pawn_moves(self, pos, piece):
        moves = []
        row, col = pos
        direction = -1 if piece.color == 'white' else 1
        # One square forward
        next_row = row + direction
        if self.in_bounds(next_row, col) and self.get_piece((next_row, col)) is None:
            moves.append((next_row, col))
            # Two squares forward on first move
            start_row = 6 if piece.color == 'white' else 1
            if row == start_row:
                next_row2 = row + 2 * direction
                if self.get_piece((next_row2, col)) is None:
                    moves.append((next_row2, col))
        # Diagonal captures (including en passant)
        for dc in [-1, 1]:
            new_col = col + dc
            if self.in_bounds(next_row, new_col):
                target = self.get_piece((next_row, new_col))
                if target is not None and target.color != piece.color:
                    moves.append((next_row, new_col))
                # En passant possibility
                if target is None and self.last_move:
                    last_start, last_end, last_piece = self.last_move
                    if last_piece.type == 'P' and abs(last_start[0] - last_end[0]) == 2:
                        if last_end[0] == row and last_end[1] == new_col:
                            moves.append((next_row, new_col))
        return moves

    def get_knight_moves(self, pos, piece):
        moves = []
        row, col = pos
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if self.in_bounds(new_row, new_col):
                target = self.get_piece((new_row, new_col))
                if target is None or target.color != piece.color:
                    moves.append((new_row, new_col))
        return moves

    def get_sliding_moves(self, pos, piece, directions):
        moves = []
        row, col = pos
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while self.in_bounds(new_row, new_col):
                target = self.get_piece((new_row, new_col))
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
                new_row += dr
                new_col += dc
        return moves

    def get_king_moves(self, pos, piece):
        moves = []
        row, col = pos
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if self.in_bounds(new_row, new_col):
                    target = self.get_piece((new_row, new_col))
                    if target is None or target.color != piece.color:
                        moves.append((new_row, new_col))
        # Castling moves
        if not piece.has_moved and not self.is_in_check(piece.color):
            if self.can_castle_kingside(piece.color):
                moves.append((row, col + 2))
            if self.can_castle_queenside(piece.color):
                moves.append((row, col - 2))
        return moves

    def can_castle_kingside(self, color):
        row = 7 if color == 'white' else 0
        king = self.get_piece((row, 4))
        rook = self.get_piece((row, 7))
        if king is None or rook is None or king.has_moved or rook.has_moved:
            return False
        # Squares between king and rook must be empty
        if self.get_piece((row, 5)) is not None or self.get_piece((row, 6)) is not None:
            return False
        # The king cannot pass through or end on an attacked square
        for col in [4, 5, 6]:
            if self.square_under_attack((row, col), color):
                return False
        return True

    def can_castle_queenside(self, color):
        row = 7 if color == 'white' else 0
        king = self.get_piece((row, 4))
        rook = self.get_piece((row, 0))
        if king is None or rook is None or king.has_moved or rook.has_moved:
            return False
        if (self.get_piece((row, 1)) is not None or 
            self.get_piece((row, 2)) is not None or 
            self.get_piece((row, 3)) is not None):
            return False
        for col in [2, 3, 4]:
            if self.square_under_attack((row, col), color):
                return False
        return True

    def square_under_attack(self, pos, color):
        enemy_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece is not None and piece.color == enemy_color:
                    moves = self.get_moves_for_piece_no_filter((row, col))
                    if pos in moves:
                        return True
        return False

    def get_moves_for_piece_no_filter(self, pos):
        """Generate moves without filtering out those that leave king in check."""
        piece = self.get_piece(pos)
        if piece is None:
            return []
        if piece.type == 'P':
            return self.get_pawn_moves(pos, piece)
        elif piece.type == 'N':
            return self.get_knight_moves(pos, piece)
        elif piece.type == 'B':
            return self.get_sliding_moves(pos, piece, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif piece.type == 'R':
            return self.get_sliding_moves(pos, piece, directions=[(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece.type == 'Q':
            return self.get_sliding_moves(pos, piece, directions=[(-1, -1), (-1, 1), (1, -1), (1, 1),
                                                                   (-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece.type == 'K':
            moves = []
            row, col = pos
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if self.in_bounds(new_row, new_col):
                        target = self.get_piece((new_row, new_col))
                        if target is None or target.color != piece.color:
                            moves.append((new_row, new_col))
            return moves
        return []

    def is_in_check(self, color):
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece is not None and piece.type == 'K' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos is not None:
                break
        if king_pos is None:
            return True
        return self.square_under_attack(king_pos, color)

    def get_all_legal_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece((row, col))
                if piece is not None and piece.color == color:
                    for move in self.get_legal_moves_for_piece((row, col)):
                        moves.append(((row, col), move))
        return moves

    def is_checkmate(self, color):
        return self.is_in_check(color) and len(self.get_all_legal_moves(color)) == 0
