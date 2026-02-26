import json
import chess
import chess.svg
from PIL import Image
from io import BytesIO
import cairosvg
import random
import os

# ------------------------------
# File paths
# ------------------------------
GAME_STATE_FILE = "game_state.json"
TILE_COUNT_FILE = "tile_count.json"
BOARD_IMAGE_FILE = "board.png"

# ------------------------------
# Reset game function
# ------------------------------
def reset_game():
    initial_fen = chess.STARTING_FEN
    json.dump({
        "fen": initial_fen,
        "turn": "white",
        "move_history": []
    }, open(GAME_STATE_FILE, "w"), indent=2)
    # Reset all clicks
    tiles = [f"{file}{rank}" for rank in range(1,9) for file in "abcdefgh"]
    json.dump({tile: 0 for tile in tiles}, open(TILE_COUNT_FILE, "w"), indent=2)
    print("Game reset!")

# ------------------------------
# Load game state
# ------------------------------
if not os.path.exists(GAME_STATE_FILE):
    reset_game()

with open(GAME_STATE_FILE, "r") as f:
    state = json.load(f)

board = chess.Board(state["fen"])

# ------------------------------
# Check for game over
# ------------------------------
if board.is_game_over():
    print(f"Game over: {board.result()}")
    reset_game()
    board = chess.Board(chess.STARTING_FEN)

# ------------------------------
# Load click counts
# ------------------------------
if not os.path.exists(TILE_COUNT_FILE):
    reset_game()

with open(TILE_COUNT_FILE, "r") as f:
    tile_counts = json.load(f)

# ------------------------------
# Community (White) turn
# ------------------------------
if board.turn == chess.WHITE:
    legal_moves = list(board.legal_moves)

    # Map moves → destination square clicks
    best_move = None
    best_score = -1
    for move in legal_moves:
        dest_square = chess.square_name(move.to_square)
        score = tile_counts.get(dest_square, 0)
        if score > best_score:
            best_score = score
            best_move = move

    if best_score > 0 and best_move:
        board.push(best_move)
        print(f"Community (White) played: {best_move.uci()}")
    else:
        print("No community clicks or no valid move; skipping turn.")

# ------------------------------
# Engine (Black) turn
# ------------------------------
if board.turn == chess.BLACK:
    legal_moves = list(board.legal_moves)
    if legal_moves:
        # Simple engine: pick random legal move
        engine_move = random.choice(legal_moves)
        board.push(engine_move)
        print(f"Engine (Black) played: {engine_move.uci()}")

# ------------------------------
# Update game state
# ------------------------------
state["fen"] = board.fen()
state["turn"] = "black" if board.turn == chess.BLACK else "white"
state["move_history"].append(board.peek().uci() if board.move_stack else None)

with open(GAME_STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)

# ------------------------------
# Reset tile counts after White move
# ------------------------------
if board.turn == chess.BLACK:
    # Clear clicks after community turn
    tiles = [f"{file}{rank}" for rank in range(1,9) for file in "abcdefgh"]
    json.dump({tile: 0 for tile in tiles}, open(TILE_COUNT_FILE, "w"), indent=2)

# ------------------------------
# Generate board image
# ------------------------------
svg_board = chess.svg.board(board=board, size=400)
png_data = cairosvg.svg2png(bytestring=svg_board.encode("utf-8"))
image = Image.open(BytesIO(png_data))
image.save(BOARD_IMAGE_FILE)
print(f"Board image saved to {BOARD_IMAGE_FILE}")
