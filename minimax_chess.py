# These imports are just to suppress pygame startup message
import contextlib
import io
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
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def display_message(text, font_size):
    font = pygame.font.SysFont('Arial', font_size)
    message = font.render(text, True, (255, 255, 255), (0, 0, 0))
    rect = message.get_rect(center=(SIDE_LENGTH // 2, SIDE_LENGTH // 2))
    screen.blit(message, rect)
    pygame.display.flip()

def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                screen.blit(pieces[piece.symbol()], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

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
#Define a function to get the list of attackers, returning a dictionary
'''def check_attackers(board, color):
    attacked_info = {}
    # For each square with a piece... 
    for square, piece in board.piece_map().items():
        if piece.color == color:
            # Get squares where enemy pieces are attacking this square
            enemy_attackers = board.attackers(not color, square)
            if enemy_attackers:
                attacked_info[square] = enemy_attackers
    return attacked_info'''

#Define a function that evaluates material and placement of pieces. This is to define the 3-depth minimax bot
def evaluate_material(board):
    # Return inf for white mate, -inf for black mate, and 0 for stalemate. 
    if board.is_checkmate():
        return -float('inf') if board.turn == chess.WHITE else float('inf')
    if board.is_stalemate():
        return 0 
    # Material values for each piece, in centipawns (so a pawn is 100/100s of a pawn)
    values = {
        chess.PAWN:   100,
        chess.KNIGHT: 300,
        chess.BISHOP: 330,
        chess.ROOK:   500,
        chess.QUEEN:  900,
        chess.KING:   0  
    }
    
    # Piece tables to promote the engine to move to certain squares and develop earlygame
    # These tables are for White, and we reverse them when calculating eval for Black
    pawn_table = [
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  20, -10,   0,   0, -10,  20,   5,
         5,  10,  10, -100, -100,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ]
    
    knight_table = [
       -50, -10,  -5, -10, -10,  -5, -10, -50,
       -10, -10,   0,   5,   5,   0, -10, -10,
       -10,  5,   25,  20,  20,  25,   5, -10,
       -10,  0,   10,  -20, -20, 10,   0, -10,
       -10,  5,   5,  -20, -20,  5,   5, -10,
       -10,  0,   25,  0,  0,  20,   0, -10,
       -10, -10,   0,   0,   0,   0, -10, -10,
       -50, -10,  -5, -10, -10,  -5, -10, -50
    ]
    
    bishop_table = [
       -30, -10, -10, -10, -10, -10, -10, -30,
       -10,   0,   0,  0,   0,   0,   0,  0,
       -10,   0,   0,  0,   0,   0,   0,  0,
       -10,   5,   0,  10,  10,  0,   5, -10,
       -10,   0,   20,  10,  10,  20,   0, -10,
        4,    0,   0,  0,   0,   0,   0,   4,
       -10,   5,   0,  0,   0,   0,   5, -10,
       -30, -10, -20, -10, -10, -20, -10, -30
    ]
    
    rook_table = [
         0,   0,   0,   0,   0,   0,   0,   0,
         10,  20,  20,  20,  20,  20,  20,   10,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         0,   0,   0,   10,   10,   3,   0,   0
    ]
    #We'd want it to prioritize open files, but right now, we can just have it take the center files and such. 
    if board.halfmove_clock <= 10:  
        queen_table = [
        -100, -100, -100,  50,  50, -100, -100, -100,
        -100, -100, -100,   100,  100,  -100,  -100, -100,
        -100, -100, -100,  -100, -100,-100,   -100, -100,
        -100, -100, -100,   -100,   -100,   -100,   -100,  -100,
        -100, -100, -100,   -100,   -100,   -100,   -100,  -100,
        -100, -100, -100,   -100,   -100,   -100,   -100, -100,
        -100, -100, -100,   -100,   -100,   -100,   -100, -100,
        -100, -100, -100,  -100,  -100, -100, -100, -100
        ]
    else: 
        queen_table = [
        -20, -10, -10,  -50,  -50, -10, -10, -20,
        -10,   0,   0,   -30,  -30,  0,   0, -10,
        -10,   10, 10,  0,   0,     10,   10, -10,
        -5,   10,   10,  30,   30,   10,   10,  -5,
        -5,   10,   10,   30,   30,   10,   10,  -5,
        20,   40,   40,   20,   20,   40,   40, 20,
        20,   40,   40,   40,   40,   40,   40, 20,
        -20, -10, -10,  -5,  -5, -10, -10, -20
        ]
    king_table = [
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -30, -40, -40, -50, -50, -40, -40, -30,
       -20, -30, -30, -40, -40, -30, -30, -20,
       -10, -20, -20, -20, -20, -20, -20, -10,
        20,  20,   0,   0,   0,   0,  20,  20,
        20,  30,  10,   0,   0,  10,  30,  20
    ]
    
    # Map each piece type to its table, using a dictionary. 
    piece_tables = {
        chess.PAWN: pawn_table,
        chess.KNIGHT: knight_table,
        chess.BISHOP: bishop_table,
        chess.ROOK: rook_table,
        chess.QUEEN: queen_table,
        chess.KING: king_table,
    }
    
    score = 0
    for square, piece in board.piece_map().items():
        # Use the material value. 
        material = values[piece.piece_type]
        # Calculate the positional bonus, and add it. 
        if piece.color == chess.WHITE:
            positional = piece_tables[piece.piece_type][square]
            score += 1.5*material + positional
        else:
            positional = piece_tables[piece.piece_type][square]
            score -= 1.5*material + positional
    return score
#Train engine to sometimes miss long moves, like a human would
def is_long_move(move):
    piece = board.piece_at(move.from_square)
    old_file = chess.square_file(move.from_square)
    old_rank = chess.square_rank(move.from_square)
    new_file = chess.square_file(move.to_square)
    new_rank = chess.square_rank(move.to_square)
    file_diff = abs(new_file - old_file)
    rank_diff = abs(new_rank - old_rank)
    if piece == 'p' or piece == 'P' or piece == 'k' or piece == 'K' or piece == 'n' or piece == 'N':
        return False 
    elif piece == 'B' or piece == 'b':
        total = rank_diff  
        weight_list = [0, 1, 1, 0.99, 0.9, 0.85, 0.7, 0.6]
    elif piece == 'r' or piece == 'R':
        total = max(rank_diff, file_diff) 
        weight_list = [0, 1, 1, 0.99, 0.95, 0.9, 0.85, 0.8]
    elif piece == 'q' or piece == 'Q':
        if file_diff > 0 and rank_diff > 0:
            total = rank_diff  
            weight_list = [0, 1, 1, 0.99, 0.9, 0.85, 0.7, 0.6]
        else:
            total = max(rank_diff, file_diff) 
            weight_list = [0, 1, 1, 0.99, 0.95, 0.9, 0.85, 0.8]
    else:
        weight_list = []
        total = 0
    if weight_list != [] and total != 0:
        if random.random() <= weight_list[total]:
            return False
        else:
            return True  
        

#Define another evaluation function, based on the first one 
def minimax(board, depth, alpha, beta, is_maximizing):
    #Base case if depth = 0, return material with some random noise 
    if depth == 0 or board.is_game_over():
        return evaluate_material(board) + random.uniform(-5, 5)
    moves = [move for move in board.legal_moves if not is_long_move(move)]
    if moves == []:
        moves = list(board.legal_moves)

    if is_maximizing:
        max_eval = -float('inf')
        for move in moves:
            board.push(move)
            #Recursion
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            #Recursion 
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Change depth=n to whatever you want below 
def engine_move_choice(board, engine_color, depth=4):
    best_move = None
    if engine_color == chess.WHITE:
        best_value = -float('inf')
        #As in, set the best value to -infinity, so it can always find a better one
        for move in board.legal_moves:
            board.push(move)
            board_value = minimax(board, depth - 1, -float('inf'), float('inf'), False)
            #print("Testing Move:", move)
            board.pop()
            if board_value > best_value:
                best_value = board_value
                best_move = move
    else:
        best_value = float('inf')
        for move in board.legal_moves:
            board.push(move)
            board_value = minimax(board, depth - 1, -float('inf'), float('inf'), True)
            #print("Testing Move:", move)
            board.pop()
            if board_value < best_value:
                best_value = board_value
                best_move = move
    if best_move is None:
        best_move = random.choice(list(board.legal_moves))
    return best_move

# --- Main game loop ---
running = True
selected_square = None
mate = False
draw = False 
saved_positions = {}

while running:
    user_color, pieces, board, screen = start_game()
    # Engine plays the opposite color to the user.
    engine_color = not user_color
    mate = False
    draw = False
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
                    if move_choice is not None:
                        board.push(move_choice)
            elif not board.is_checkmate() and not board.is_stalemate():
                if len(board.piece_map()) <= 3:
                    board.push(engine_move_choice(board, engine_color, depth=8))
                elif len(board.piece_map()) > 3:
                    board.push(engine_move_choice(board, engine_color, depth=3))
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
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(highlight_col * SQUARE_SIZE, highlight_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.display.flip()
    if mate and board.turn == chess.WHITE:
        display_message("Black wins! Press r to continue", 24)
        while mate:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.unicode.lower() == 'r':
                    mate = False 
    elif mate and board.turn == chess.BLACK:
        display_message("White wins! Press r to continue", 24)
        while mate:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.unicode.lower() == 'r':
                    mate = False 
    elif draw: 
        display_message("Stalemate! It's a draw. Press r to continue", 24)
        while draw:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.unicode.lower() == 'r':
                    draw = False 
print("Forcequit successfully")
