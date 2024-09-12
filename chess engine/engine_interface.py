import chess
import chess.engine
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

def get_engine_move(fen, skill_level=20):
    # Path to the Stockfish executable
    engine_path = config['current_engine_path']
    print(engine_path)
    board = chess.Board(fen)
    
    # Start the Stockfish engine
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        # Set the skill level
        engine.configure({"Skill Level": skill_level})
        
        # Get the move
        result = engine.play(board, chess.engine.Limit(time=1.0))
        move = result.move
        print(move)

    return move.uci()


