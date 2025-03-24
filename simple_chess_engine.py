# Importing our stuff
import chess
import chess.svg
import random 
# So we know who got mated, we define the bot_mate variable
bot_mate = False 
# Set up the board
board = chess.Board()
# Define the random_move_modified algorithm, which picks a random move that does not allow mate. 
def random_move_modified(board, legal_moves):
    # We define the list of moves that won't allow mate in 1. 
    not_dying_moves = []
    # We iterate through every legal move, finding the legal moves for our opponent.
    for move in legal_moves:
        board_future = board.copy()
        board_future.push_san(move)
        opponent_next_move = list(board_future.legal_moves)
        san_legal_opponent_next_moves = [board_future.san(opp) for opp in opponent_next_move]
        for opp_san in san_legal_opponent_next_moves:
            # Checks for the "#" indicating mate in chess notation. 
            if '#' in opp_san:
                break
        # If it doesn't lead to mate, append the move. 
        not_dying_moves.append(move)
    # This could be a debug line:
    #print("didn't die on:", not_dying_moves)
    # So here, we pick a random legal move that doesn't allow mate, if there are any. 
    if not_dying_moves != []:
        not_dying_move_choice = random.choice(not_dying_moves)
        return not_dying_move_choice 
    # If there are none, we pick any random legal move. 
    else:
        return random.choice(legal_moves)
# move() is actually how we make the move. We can write multiple algorithms, but the structure for move() will stay the same
def move(board, san_legal_moves):
    if san_legal_moves == []:
        return "Checkmate!"
    else:
        return random_move_modified(board, san_legal_moves)

print("btw castling is O-O, the letter O.")
# If it isn't checkmate...
while not(board.is_checkmate()):
    # Find the legal moves for the player
    legal_moves_user = list(board.legal_moves)
    san_legal_moves_user = [board.san(move) for move in legal_moves_user]
    # Print the board, which is neccesary for getting the user's move
    print(board)
    while True:
        # Take the user's input for their choice of move.
        user_move = input("Which Move?")
        # If it's legal, make the move and note that the user has picked a legal move and we can break
        if user_move in san_legal_moves_user:
            board.push_san(user_move)
            break
        # Else, continue the loop.
        else:
            print("That move is illegal!")
    # Calculate the legal moves for the bot and pass it to move(). 
    legal_moves_bot = list(board.legal_moves)
    san_legal_moves_bot = [board.san(move) for move in legal_moves_bot]
    bot_move = move(board, san_legal_moves_bot)
    # If it isn't checkmate, tell the user what the bot moved. 
    if bot_move != "Checkmate!":
        print("Bot moved:", bot_move)
        board.push_san(bot_move)
    # If it is, print the ending position. 
    else:
        print("Bot got mated!")
        print(board)
        bot_mate = True 
        break 
# If the bot didn't get mated, and it's checkmate, you got mated!
if not(bot_mate): 
    print(board)
    print("You got mated!")
