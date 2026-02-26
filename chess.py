import json
import chess
import chess.svg
from PIL import Image
from io import BytesIO
import cairosvg

# ------------------------------
# File paths
# ------------------------------
GAME_STATE_FILE = "game_state.json"
TILE_COUNT_FILE = "tile_count.json"
BOARD_IMAGE_FILE = "board.png"

# ------------------------------
# Load game state
# ------------------------------
with open(GAME_STATE_FILE, "r") as f:
    state = json.load(f)

board = chess.Board(state["fen"])

# ------------------------------
# Load click counts
# ------------------------------
with open(TILE_COUNT_FILE, "r") as f:
    tile_counts = json.load(f)

# ------------------------------
# Find best move (most clicked destination square)
# ------------------------------
legal_moves = list(board.legal_moves)

best_move = None
best_score = -1

for move in legal_moves:
    dest_square = chess.square_name(move.to_square)
    score = tile_counts.get(dest_square, 0)
    if score > best_score:
        best_score = score
        best_move = move

# ------------------------------
# Play move if available
# ------------------------------
if best_move:
    board.push(best_move)
    print(f"Played move: {best_move.uci()}")
else:
    print("No legal moves found.")

# ------------------------------
# Update game state
# ------------------------------
state["fen"] = board.fen()
state["turn"] = "black" if board.turn == chess.BLACK else "white"
state["move_history"].append(best_move.uci() if best_move else None)

with open(GAME_STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)

# ------------------------------
# Generate board image
# ------------------------------
# Create SVG of board
svg_board = chess.svg.board(board=board, size=400)

# Convert SVG to PNG
png_data = cairosvg.svg2png(bytestring=svg_board.encode("utf-8"))
image = Image.open(BytesIO(png_data))
image.save(BOARD_IMAGE_FILE)

print(f"Board image saved to {BOARD_IMAGE_FILE}")
