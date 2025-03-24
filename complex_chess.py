# These imports are just to suppress pygame startup message
import contextlib
import io
# Actually important libraries:
with contextlib.redirect_stdout(io.StringIO()):
    import pygame
import chess
import random 

# Initialize pygame
pygame.init()

# Constants
SIDE_LENGTH = 640
SQUARE_SIZE = SIDE_LENGTH // 8

# Colors
WHITE = (238, 238, 210)
BROWN = (118, 150, 86)
HIGHLIGHT = (186, 202, 68)

# Load chess piece assets
def load_pieces():
    pieces = {}
    piece_names = ['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K']
    file_names = ['p', 'n', 'b', 'r', 'q', 'k', 'wp', 'wn', 'wb', 'wr', 'wq', 'wk']
    for name in piece_names:
        pieces[name] = pygame.transform.scale(
            pygame.image.load(f"Assets/{file_names[piece_names.index(name)]}.png"),
            (SQUARE_SIZE, SQUARE_SIZE),
        )
    return pieces

pieces = load_pieces()
board = chess.Board()
screen = pygame.display.set_mode((SIDE_LENGTH, SIDE_LENGTH))
pygame.display.set_caption('Chess Board')

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def display_message(text, font_size):
    font = pygame.font.SysFont('Arial', font_size)
    message = font.render(text, True, (255, 255, 255), (0, 0, 0))
    rect = message.get_rect(center=(SIDE_LENGTH // 2, SIDE_LENGTH // 2))
    screen.blit(message, rect)
    pygame.display.flip()

def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7-row)
            piece = board.piece_at(square)
            if piece:
                screen.blit(pieces[piece.symbol()], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def choose_promotion():
    display_message("Press Q (Queen), R (Rook), B (Bishop), or N (Knight)", 18)
    promotion = None
    while promotion not in ['q', 'r', 'b', 'n']:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode.lower() in ['q', 'r', 'b', 'n']:
                    promotion = event.unicode.lower()
    return {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}[promotion]
def start_game():
    pieces = load_pieces()
    board = chess.Board()
    screen = pygame.display.set_mode((SIDE_LENGTH, SIDE_LENGTH))
    pygame.display.set_caption('Chess Board')
    draw_board()
    draw_pieces(board)
    display_message("What color do you want to play? w (White) b (Black)", 27)
    user = None
    while user not in ['w', 'b']:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode.lower() in ['w', 'b']:
                    user = event.unicode.lower()
    return {'w': chess.WHITE, 'b': chess.BLACK}[user], pieces, board, screen

def user_move_choice(board, event, selected_square):
    move = None
    file, rank = pygame.mouse.get_pos()[0] // SQUARE_SIZE, pygame.mouse.get_pos()[1] // SQUARE_SIZE
    clicked_square = chess.square(file, 7 - rank)

    if selected_square is None:
        selected_square = clicked_square if board.piece_at(clicked_square) else None
    else:
        move = chess.Move(selected_square, clicked_square)

        # Castling handling
        if board.piece_at(selected_square).piece_type == chess.KING and abs(chess.square_file(selected_square) - chess.square_file(clicked_square)) > 1:
            if chess.square_file(clicked_square) == 6:
                move = chess.Move(selected_square, chess.square(6, chess.square_rank(selected_square)))
            elif chess.square_file(clicked_square) == 2:
                move = chess.Move(selected_square, chess.square(2, chess.square_rank(selected_square)))

        # Pawn Promotion handling
        is_promotion = board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(clicked_square) in [0, 7]
        if is_promotion:
            possible_promos = [chess.Move(selected_square, clicked_square, p) for p in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]]
            legal_promos = [m for m in possible_promos if m in board.legal_moves]

            if legal_promos:
                promo_choice = choose_promotion()
                move = chess.Move(selected_square, clicked_square, promotion=promo_choice)

        if move not in board.legal_moves:
            move = None
        selected_square = None

    return move, selected_square

def engine_move_choice(board):
    return random.choice(list(board.legal_moves))
running = True
selected_square = None
mate = False
draw = False 
#Main loop
while running:
    user_color, pieces, board, screen = start_game()
    while not mate and not draw and running:
        draw_board()
        draw_pieces(board)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode.lower() == 'q':
                    running = False 
            if event.type == pygame.QUIT:
                running = False 
            if board.turn == user_color:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    move_choice, selected_square = user_move_choice(board, event, selected_square)
                    if move_choice != None:
                        board.push(move_choice)
            elif not board.is_checkmate():
                board.push(engine_move_choice(board))
        if board.is_checkmate():
            draw_board()
            draw_pieces(board)
            mate = True
        if board.is_stalemate():
            draw_board()
            draw_pieces(board)
            draw = True
        if selected_square is not None:
            highlight_col, highlight_row = chess.square_file(selected_square), 7 - chess.square_rank(selected_square)
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(highlight_col*SQUARE_SIZE, highlight_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.display.flip()
    if mate and board.turn == chess.WHITE:
        display_message("Black wins! Press r to continue", 24)
        while mate == True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.unicode.lower() == 'r':
                        mate = False 
    elif mate and board.turn == chess.BLACK:
        display_message("White wins! Press r to continue", 24)
        while mate == True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.unicode.lower() == 'r':
                        mate = False 
    elif draw: 
        display_message("Stalemate! It's a draw. Press r to continue", 24)
        while draw == True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.unicode.lower() == 'r':
                        draw = False 
print("Forcequit successfully")