import chess
import tkinter as tk

board = chess.Board()  # Initialize the chess board
window = tk.Tk()
window.geometry("600x600")
squareSize = 600 // 8
canvas = tk.Canvas(window, width=8 * squareSize, height=8 * squareSize)
canvas.pack()

playerColour = chess.WHITE  # Default player color

# Mapping of piece symbols
pieceImages = {
    'p': "♙", 'P': "♟",
    'n': "♘", 'N': "♞",
    'b': "♗", 'B': "♝",
    'r': "♖", 'R': "♜",
    'q': "♕", 'Q': "♛",
    'k': "♔", 'K': "♚",
}

# Mapping of board coordinates to algebraic notation
squareLib = {(x, y): chr(ord('a') + x) + str(8 - y) for x in range(8) for y in range(8)}

selectedSquare = None  # Track the currently selected square

def placePiece(x, y, piece):
    """Place a chess piece on the board at the specified (x, y) coordinates."""
    if piece in pieceImages:
        canvas.create_text(
            x * squareSize + squareSize // 2,
            y * squareSize + squareSize // 2,
            text=pieceImages[piece],
            font=('Arial', int(squareSize * 0.6)),
            fill='black'
        )

def drawBoard(fen):
    """Draw the chess board and pieces based on the FEN string."""
    canvas.delete('all')  # Clear the canvas
    
    # Generate the board squares
    for y in range(8):
        for x in range(8):
            colour = 'white' if (x + y) % 2 == 0 else 'grey'
            canvas.create_rectangle(
                x * squareSize, y * squareSize,
                (x + 1) * squareSize, (y + 1) * squareSize,
                fill=colour, outline='black'
            )
    
    # Draw pieces
    rows = fen.split()[0].split('/')
    for y in range(8):
        row = rows[7 - y] if playerColour == chess.WHITE else rows[y]
        if playerColour == chess.BLACK:
            row = row[::-1]  # Reverse the row for black player
        x = 0
        for char in row:
            if char.isdigit():
                x += int(char)  # Skip empty squares
            else:
                placePiece(x, y, char)
                x += 1
    
    if len(rows) != 8:
        print("Error: FEN string does not have exactly 8 rows.")


def handleClick(event):
    """Handle mouse clicks on the chessboard."""
    global selectedSquare
    x = event.x // squareSize
    y = event.y // squareSize
    
    if playerColour == chess.BLACK:
        x, y = 7 - x, 7 - y  # Adjust for black player's perspective

    square = squareLib[(x, y)]
    print(f"Clicked on: {square}, Selected: {selectedSquare}")  # Debugging output

    if selectedSquare:
        fromSquare = squareLib[selectedSquare]
        move = chess.Move.from_uci(f"{fromSquare}{square}")
        if move in board.legal_moves:
            board.push(move)  
            drawBoard(board.fen()) 
        else:
            print(f"Invalid move: {move}")  # Debugging output for invalid moves
        selectedSquare = None  
    else:
        selectedSquare = (x, y)  

def showColourSelection():
    """Show a dialog for the user to select their colour."""
    global playerColour
    colourWindow = tk.Toplevel(window)
    colourWindow.title  ("Select Colour")
    
    def setColour(colour):
        global playerColour
        playerColour = chess.WHITE if colour == 'white' else chess.BLACK
        colourWindow.destroy()
        drawBoard(board.fen())  # Update the board after colour selection
    
    tk.Button(colourWindow, text="Play as White", command=lambda: setColour('white')).pack(pady=5)
    tk.Button(colourWindow, text="Play as Black", command=lambda: setColour('black')).pack(pady=5)

canvas.bind("<Button-1>", handleClick)  # Bind mouse clicks to the handleClick function

showColourSelection()  # Show the colour selection dialog
window.mainloop()  # Start the Tkinter event loop
