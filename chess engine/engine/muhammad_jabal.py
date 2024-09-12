import chess
import numpy

board = chess.Board()

pieceValues = {
               'P': 100,   # White Pawn
               'N': 300,   # White Knight
               'B': 330,   # White Bishop
               'R': 500,   # White Rook
               'Q': 900,   # White Queen
               'K': 99999,   # White King 
               'p': -100,  # Black Pawn
               'n': -300,  # Black Knight
               'b': -330,  # Black Bishop
               'r': -500,  # Black Rook
               'q': -900,  # Black Queen
               'k': -99999    # Black King
              }

def determine_game_phase(board):
    # Material counts to determine game phase
    phase_score = 0

    # Count material for determining game phase
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            symbol = piece.symbol()
            if symbol in 'Pp':
                phase_score += 1
            elif symbol in 'NnBb':
                phase_score += 3
            elif symbol in 'Rr':
                phase_score += 5
            elif symbol in 'Qq':
                phase_score += 9

    # Set phase thresholds (tune these as needed)
    if phase_score > 30:
        return 'opening'
    elif phase_score > 15:
        return 'middlegame'
    else:
        return 'endgame'

def invert_table(table):
    return [row[::-1] for row in table[::-1]]

# Pawn piece-square table
PAWN_TABLE = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [  5,  10,  10, -20, -20,  10,  10,   5],
    [  5,  -5, -10,   0,   0, -10,  -5,   5],
    [  0,   0,   0,  20,  20,   0,   0,   0],
    [  5,   5,  10,  25,  25,  10,   5,   5],
    [ 10,  10,  20,  30,  30,  20,  10,  10],
    [ 50,  50,  50,  50,  50,  50,  50,  50],
    [  0,   0,   0,   0,   0,   0,   0,   0]
]

PAWN_TABLE_BLACK = invert_table(PAWN_TABLE)

# Knight piece-square table
KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

KNIGHT_TABLE_BLACK = invert_table(KNIGHT_TABLE)

# Bishop piece-square table
BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

BISHOP_TABLE_BLACK = invert_table(BISHOP_TABLE)

# Rook piece-square table
ROOK_TABLE = [
    [  0,   0,   0,   5,   5,   0,   0,   0],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [  5,  10,  10,  10,  10,  10,  10,   5],
    [  0,   0,   0,   0,   0,   0,   0,   0]
]

ROOK_TABLE_BLACK = invert_table(ROOK_TABLE)

# Queen piece-square table
QUEEN_TABLE = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [  0,   0,   5,   5,   5,   5,   0,  -5],
    [ -5,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20]
]

QUEEN_TABLE_BLACK = invert_table(QUEEN_TABLE)

# King piece-square table (middle game)
KING_TABLE_MIDDLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [ 20,  20,   0,   0,   0,   0,  20,  20],
    [ 20,  30,  10,   0,   0,  10,  30,  20]
]

KING_TABLE_MIDDLE_BLACK = invert_table(KING_TABLE_MIDDLE)

# King piece-square table (end game)
KING_TABLE_END = [
    [-50, -30, -30, -30, -30, -30, -30, -50],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-50, -40, -30, -20, -20, -30, -40, -50]
]

KING_TABLE_END_BLACK = invert_table(KING_TABLE_END)

def evaluate_board(board):
    score = 0
    game_phase = determine_game_phase(board)  # Compute game phase once

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        symbol = piece.symbol()
        row = chess.square_rank(square)
        col = chess.square_file(square)

        # Material value and Piece-Square Table value
        if symbol == 'P':
            score += pieceValues[symbol]  # White pawn
            score += PAWN_TABLE[7 - row][col]  # Use 7 - row for proper indexing
        elif symbol == 'N':
            score += pieceValues[symbol]  # White knight
            score += KNIGHT_TABLE[7 - row][col]
        elif symbol == 'B':
            score += pieceValues[symbol]  # White bishop
            score += BISHOP_TABLE[7 - row][col]
        elif symbol == 'R':
            score += pieceValues[symbol]  # White rook
            score += ROOK_TABLE[7 - row][col]
        elif symbol == 'Q':
            score += pieceValues[symbol]  # White queen
            score += QUEEN_TABLE[7 - row][col]
        elif symbol == 'K':
            score += pieceValues[symbol]  # White king
            if game_phase in ['opening', 'middlegame']:
                score += KING_TABLE_MIDDLE[7 - row][col]
            else:
                score += KING_TABLE_END[7 - row][col]
        elif symbol == 'p':
            score += pieceValues[symbol]  # Black pawn
            score += PAWN_TABLE_BLACK[row][col]  # Direct indexing for Black pieces
        elif symbol == 'n':
            score += pieceValues[symbol]  # Black knight
            score += KNIGHT_TABLE_BLACK[row][col]
        elif symbol == 'b':
            score += pieceValues[symbol]  # Black bishop
            score += BISHOP_TABLE_BLACK[row][col]
        elif symbol == 'r':
            score += pieceValues[symbol]  # Black rook
            score += ROOK_TABLE_BLACK[row][col]
        elif symbol == 'q':
            score += pieceValues[symbol]  # Black queen
            score += QUEEN_TABLE_BLACK[row][col]
        elif symbol == 'k':
            score += pieceValues[symbol]  # Black king
            if game_phase in ['opening', 'middlegame']:
                score += KING_TABLE_MIDDLE_BLACK[row][col]
            else:
                score += KING_TABLE_END_BLACK[row][col]

    return score

print(evaluate_board(board))

