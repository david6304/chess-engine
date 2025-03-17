# gui.py
import pygame
from game import Game
import os

# Colors and board dimensions remain the same
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

SQUARE_SIZE = 80
BOARD_SIZE = 8 * SQUARE_SIZE

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        pygame.display.set_caption("Chess Engine")
        # Load piece images
        self.piece_images = self.load_piece_images()
        self.game = Game()
        self.selected = None
        self.legal_moves = []

    def load_piece_images(self):
        piece_images = {}
        base_path = os.path.join("..", "assets", "images")
        pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
        for color in ['w', 'b']:
            for piece in pieces:
                filename = os.path.join(base_path, f"{color}{piece}.png")
                image = pygame.image.load(filename)
                # Scale the image to fit the square size
                image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
                piece_images[color + piece] = image
        return piece_images

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        board = self.game.board.board
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece:
                    key = ('w' if piece.color == 'white' else 'b') + piece.type
                    if key in self.piece_images:
                        self.screen.blit(self.piece_images[key], (col * SQUARE_SIZE, row * SQUARE_SIZE))
                    else:
                        # Fallback: render text if image not found
                        font = pygame.font.SysFont("Arial", 40)
                        text = font.render(piece.type, True, BLACK if piece.color == 'white' else WHITE)
                        text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE / 2,
                                                          row * SQUARE_SIZE + SQUARE_SIZE / 2))
                        self.screen.blit(text, text_rect)

    def highlight_squares(self):
        for move in self.legal_moves:
            row, col = move
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(GREEN)
            self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game.game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = mouse_x // SQUARE_SIZE
                    row = mouse_y // SQUARE_SIZE
                    pos = (row, col)
                    if self.selected:
                        if pos in self.legal_moves:
                            self.game.make_move(self.selected, pos)
                        self.selected = None
                        self.legal_moves = []
                    else:
                        piece = self.game.board.get_piece(pos)
                        if piece and piece.color == self.game.current_turn:
                            self.selected = pos
                            self.legal_moves = self.game.get_legal_moves(pos)

            self.draw_board()
            if self.selected:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(RED)
                row, col = self.selected
                self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                self.highlight_squares()
            self.draw_pieces()
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()
