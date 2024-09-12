import chess
from chessboard import display
import pygame
import sys
import engine_interface
import time
import tkinter as tk
from tkinter import filedialog, simpledialog
import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'engine_paths': [],
        'current_engine_path': None
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

# Initialize pygame
pygame.init()

# Setup constants
WINDOW_SIZE = (420, 420)
SQUARE_SIZE = 50
DELAY_TIME = 1.0  # Delay time in seconds between player and computer moves
POPUP_SIZE = (200, 120)  # Size for the game end popup window

square_lib = {(x, y): chr(ord('a') + x) + str(8 - y) for x in range(8) for y in range(8)}

# Create main game window
main_window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Chess Game')
main_clock = pygame.time.Clock()

# List to store engine paths
engine_paths = []

current_engine_path = None

selected_piece = None

def show_start_menu():
    start_menu_running = True
    while start_menu_running:
        main_window.fill((200, 200, 200))  # Fill the background with white
        
        # Draw menu title
        font = pygame.font.Font(None, 74)
        title_text = font.render('Chess Game', True, (0, 0, 0))
        main_window.blit(title_text, (60, 50))
        
        # Draw buttons
        button_font = pygame.font.Font(None, 36)
        start_button = pygame.Rect(220, 150, 180, 50)
        options_button = pygame.Rect(20, 150, 180, 50)
        
        pygame.draw.rect(main_window, (100, 100, 100), start_button)
        pygame.draw.rect(main_window, (100, 100, 100), options_button)
        
        start_text = button_font.render('Start Game', True, (0, 0, 0))
        options_text = button_font.render('Options', True, (0, 0, 0))
        main_window.blit(start_text, (start_button.x + 30, start_button.y + 10))
        main_window.blit(options_text, (options_button.x + 40, options_button.y + 10))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if start_button.collidepoint(x, y):
                    start_menu_running = False
                elif options_button.collidepoint(x, y):
                    show_options_menu()

def ask_for_color():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    game_mode = simpledialog.askstring(
        "Game Mode", "Choose game mode:\n1. Two Engines\n2. Two Humans\n3. Engine vs Human"
    )

    if game_mode == '1':
        player1_type, player2_type = 'engine', 'engine'
        player1_colour = 'white'
        player2_colour = 'black'
    elif game_mode == '2':
        player1_type, player2_type = 'human', 'human'
        player1_colour = 'white'
        player2_colour = 'black'
    elif game_mode == '3':
        player1_type = simpledialog.askstring("Player 1 Type", "Is Player 1 a 'human' or an 'engine'?")
        player2_type = 'human' if player1_type == 'engine' else 'engine'
        player1_colour = simpledialog.askstring("Player 1 Color", "Choose color for Player 1 ('white' or 'black')")
        player2_colour = 'black' if player1_colour == 'white' else 'white'
    else:
        return None  # Invalid input, can handle this case as needed

    return (player1_type, player1_colour), (player2_type, player2_colour)

def prompt_for_promotion():
    popup_root = tk.Tk()
    popup_root.title('Promote Pawn')
    popup_root.geometry('100x200')
    popup_root.configure(bg='lightgrey')
    
    tk.Label(popup_root, text='Promote Pawn', bg='lightgrey', font=('Arial', 12)).pack(pady=10)
    
    promotion_buttons = {
        'q': 'Queen',
        'r': 'Rook',
        'b': 'Bishop',
        'n': 'Knight'
    }
    
    def on_button_click(promotion_piece):
        global selected_piece
        selected_piece = promotion_piece
        popup_root.destroy()
    
    selected_piece = None
    for piece, text in promotion_buttons.items():
        tk.Button(popup_root, text=text, command=lambda p=piece: on_button_click(p), width=10).pack(pady=5)
    
    popup_root.mainloop()
    print(selected_piece)
    return selected_piece

def show_game_end_popup(message):
    popup_root = tk.Tk()
    popup_root.title('Game Over')
    popup_root.geometry(f'{POPUP_SIZE[0]}x{POPUP_SIZE[1]}')
    popup_root.configure(bg='lightgrey')
    
    tk.Label(popup_root, text=message, bg='lightgrey', font=('Arial', 12)).pack(pady=10)
    
    tk.Button(popup_root, text='Play Again', command=lambda: (reset_game(), popup_root.destroy()), width=10).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(popup_root, text='Exit', command=sys.exit, width=10).pack(side=tk.RIGHT, padx=10, pady=10)
    
    popup_root.mainloop()

def reset_game():
    global board, fen, selected_square1, selected_square2, player_color, player1, player2, game_board
    board = chess.Board()
    fen = chess.STARTING_FEN
    selected_square1 = None
    selected_square2 = None
    player1, player2 = ask_for_color()
    player_color = chess.WHITE if player1[1] == 'white' else chess.BLACK
    game_board = display.start()
    if player_color == chess.BLACK:
        display.flip(game_board)

def square_check(x, y):
    if 10 < x < 410 and 10 < y < 410:
        x = (x - 10) // SQUARE_SIZE
        y = (y - 10) // SQUARE_SIZE
        if player_color == chess.BLACK:
            x = 7 - x
            y = 7 - y
        square = square_lib[(x, y)]
        return square
    else:
        print('You didn’t click a square')

def make_move(board, square1, square2):
    if square1 == square2:
        print('Null move detected: Start and end squares are the same')
        return board.fen()

    move = chess.Move.from_uci(square1 + square2)
    
    if board.piece_at(chess.parse_square(square1)) and board.piece_at(chess.parse_square(square1)).piece_type == chess.PAWN and (square2[1] == '1' or square2[1] == '8'):
        promotion_piece = prompt_for_promotion()
        print('bbb')
        if promotion_piece:
            move = chess.Move.from_uci(square1 + square2 + promotion_piece)
            print(move)
        else:
            print('aaa')
            return board.fen()
    
    if move in board.legal_moves:
        board.push(move)
        return board.fen()
    else:
        print('Illegal Move')
        return board.fen()

def check_if_game_end():
    if board.is_checkmate():
        return 'Black wins by Checkmate' if board.turn == chess.WHITE else 'White Wins by Checkmate'
    elif board.is_insufficient_material():
        return 'Draw By Insufficient Material'
    elif board.is_fivefold_repetition():
        return 'Draw By Repetition'
    elif board.is_fifty_moves():
        return 'Draw By Fifty Move Rule'
    elif board.is_stalemate():
        return 'Draw By Stalemate'
    else:
        return None

def show_options_menu():
    def upload_engine():
        file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if file_path:
            if file_path not in engine_paths:
                engine_paths.append(file_path)
                config['engine_paths'] = engine_paths
                save_config(config)
                update_option_menu()
            else:
                tk.messagebox.showinfo("Info", "Engine already added.")

    def select_engine(selected_engine):
        global current_engine_path
        for path in engine_paths:
            if os.path.split(path)[1] == selected_engine:
                current_engine_path = path
                config['current_engine_path'] = current_engine_path
                save_config(config)
                break

    options_root = tk.Tk()
    options_root.title('Options')
    options_root.geometry('400x300')
    options_root.configure(bg='lightgrey')

    tk.Label(options_root, text='Options Menu', bg='lightgrey', font=('Arial', 16)).pack(pady=10)

    tk.Label(options_root, text='Upload Engine:', bg='lightgrey', font=('Arial', 12)).pack(pady=5)
    tk.Button(options_root, text='Upload', command=upload_engine, width=10).pack(pady=5)

    tk.Label(options_root, text='Select Engine:', bg='lightgrey', font=('Arial', 12)).pack(pady=5)

    selected_engine = tk.StringVar(options_root)

    # Load engine paths from config
    engine_paths = config.get('engine_paths', [])
    
    
    # Set the current engine path from the config if available
    if engine_paths:
        if config.get('current_engine_path') in engine_paths:
            selected_engine.set(os.path.split(config['current_engine_path'])[1])
        else:
            # Set the first engine in the list as the default
            current_engine_path = engine_paths[0]
            config['current_engine_path'] = current_engine_path
            selected_engine.set(os.path.split(current_engine_path)[1])
            save_config(config)

        engine_menu = tk.OptionMenu(options_root, selected_engine, *[os.path.split(path)[1] for path in engine_paths])
    else:
        selected_engine.set('No engines available')
        engine_menu = tk.OptionMenu(options_root, selected_engine, 'No engines available')

    engine_menu.pack(pady=5)

    def update_option_menu():
        engine_menu['menu'].delete(0, 'end')
        for path in engine_paths:
            engine_menu['menu'].add_command(label=os.path.split(path)[1], command=tk._setit(selected_engine, os.path.split(path)[1]))

    tk.Button(options_root, text='Save', command=lambda: options_root.destroy(), width=10).pack(pady=10)

    options_root.mainloop()

def main():
    global board, fen, selected_square1, selected_square2, player_color, player1, player2, game_board
    board = chess.Board()
    fen = chess.STARTING_FEN
    selected_square1 = None
    selected_square2 = None
    player1, player2 = ask_for_color()
    player_color = chess.WHITE if player1[1] == 'white' else chess.BLACK
    game_board = display.start()
    if player_color == chess.BLACK:
        display.flip(game_board)

    running = True
    while running:
        main_clock.tick(30)

        # Handle events (like quitting the game)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and player1[0] == 'human' and player2[0] == 'human':
                x, y = pygame.mouse.get_pos()
                square = square_check(x, y)
                if not selected_square1:
                    selected_square1 = square
                else:
                    selected_square2 = square
                    fen = make_move(board, selected_square1, selected_square2)
                    selected_square1 = None
                    selected_square2 = None
                    display.update(fen, game_board)
                    time.sleep(DELAY_TIME)
                    
                    # Check if the game has ended
                    end_message = check_if_game_end()
                    if end_message:
                        show_game_end_popup(end_message)
                        reset_game()
                        continue

        # Continuously handle engine moves
        if (board.turn == chess.WHITE and player1[0] == 'engine') or (board.turn == chess.BLACK and player2[0] == 'engine'):
            engine_move = engine_interface.get_engine_move(board.fen())
            board.push_uci(engine_move)
            fen = board.fen()
            display.update(fen, game_board)
            time.sleep(DELAY_TIME)

            # Check if the game has ended
            end_message = check_if_game_end()
            if end_message:
                show_game_end_popup(end_message)
                reset_game()
                continue

        pygame.display.update()

show_start_menu()
main()
