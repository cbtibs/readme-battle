#!/usr/bin/env python3
import random
import os

# Board dimensions for a 6x5 grid.
BOARD_ROWS = 6
BOARD_COLS = 5

# Files for state and output.
STATE_FILE = "battle_state.txt"
OUTPUT_FILE = "battle_map.txt"

def create_initial_board():
    """
    Create a 6x5 board.
    For rows 0-2: advantage to A (3 A's then 2 B's).
    For rows 3-5: advantage to B (2 A's then 3 B's).
    """
    board = []
    for r in range(BOARD_ROWS):
        if r < BOARD_ROWS // 2:
            row = ['A'] * 3 + ['B'] * (BOARD_COLS - 3)
        else:
            row = ['A'] * (BOARD_COLS - 3) + ['B'] * 3
        board.append(row)
    return board

def default_state():
    """Return default wins (with days counter and record) and initial board."""
    wins = {'A': 0, 'B': 0, 'DAYS': 0, 'RECORD': 0}
    board = create_initial_board()
    return wins, board

def load_state():
    """
    Load the state from STATE_FILE.
    Expected format:
      Line 1: "WINS A:x B:y DAYS:z RECORD:w"
      Next BOARD_ROWS lines: raw board state (each line exactly BOARD_COLS characters).
    If file is missing or malformed, return default state.
    """
    if not os.path.exists(STATE_FILE):
        return default_state()
    try:
        with open(STATE_FILE, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        if len(lines) < 1 + BOARD_ROWS:
            return default_state()
        # Parse win tally, days, and record from the first line.
        # Expected tokens: ["WINS", "A:x", "B:y", "DAYS:z", "RECORD:w"]
        parts = lines[0].split()
        wins = {}
        for part in parts[1:]:
            key, count = part.split(':')
            wins[key] = int(count)
        # Ensure 'DAYS' and 'RECORD' exist.
        if 'DAYS' not in wins:
            wins['DAYS'] = 0
        if 'RECORD' not in wins:
            wins['RECORD'] = 0
        # Read board state from next BOARD_ROWS lines.
        board_lines = lines[1:1+BOARD_ROWS]
        if any(len(line) != BOARD_COLS for line in board_lines):
            return default_state()
        board = [list(line) for line in board_lines]
        return wins, board
    except Exception:
        return default_state()

def save_state(wins, board):
    """
    Save the state to STATE_FILE.
    Format:
      Line 1: "WINS A:x B:y DAYS:z RECORD:w"
      Next BOARD_ROWS lines: board rows.
    """
    with open(STATE_FILE, 'w') as f:
        f.write(f"WINS A:{wins['A']} B:{wins['B']} DAYS:{wins['DAYS']} RECORD:{wins['RECORD']}\n")
        for row in board:
            f.write("".join(row) + "\n")

def generate_ascii_board(board, wins):
    """
    Generate an ASCII representation of the board using box-drawing characters,
    with a header displaying the current win tally, current battle days, and record.
    """
    cell_width = 5
    num_cols = len(board[0])
    
    header = f"Wins - A: {wins['A']} | B: {wins['B']}\nDays: {wins['DAYS']}   Record: {wins['RECORD']}\n\n"
    
    top_border = "┌" + "┬".join("─" * cell_width for _ in range(num_cols)) + "┐"
    middle_border = "├" + "┼".join("─" * cell_width for _ in range(num_cols)) + "┤"
    bottom_border = "└" + "┴".join("─" * cell_width for _ in range(num_cols)) + "┘"
    
    lines = [header, top_border]
    for i, row in enumerate(board):
        row_line = "│" + "│".join(cell.center(cell_width) for cell in row) + "│"
        lines.append(row_line)
        if i < len(board) - 1:
            lines.append(middle_border)
    lines.append(bottom_border)
    
    return "\n".join(lines)

def is_row_uniform(row):
    """Return True if all cells in the row are identical."""
    return all(cell == row[0] for cell in row)

def simulate_battle():
    """
    Simulate one battle step on a random row.
    If a row becomes uniform (all A's or all B's):
      - Increment that faction's win tally.
      - Reset the days counter to 0.
      - Output a winning message with the final board state.
      - Reset the board.
    Otherwise:
      - Increment the days counter by 1.
      - Update the record if the current DAYS exceeds it.
      - Simulate a move by shifting the boundary left or right.
    Returns the ASCII output.
    """
    wins, board = load_state()
    row_index = random.randint(0, BOARD_ROWS - 1)
    row = board[row_index]
    
    try:
        boundary = max(i for i, cell in enumerate(row) if cell == 'A')
    except ValueError:
        boundary = -1

    ascii_output = ""
    # Check win condition before making a move.
    if boundary == BOARD_COLS - 1 or boundary == -1:
        winner = 'A' if boundary == BOARD_COLS - 1 else 'B'
        message = f"Faction {winner} wins on row {row_index + 1}!"
        final_state = generate_ascii_board(board, wins)
        wins[winner] += 1  # Increment win tally.
        wins['DAYS'] = 0  # Reset days counter.
        board = create_initial_board()  # Reset board.
        reset_state = generate_ascii_board(board, wins)
        ascii_output = (message + "\n\nFinal board state:\n" + final_state +
                        "\n\nBoard reset to initial state:\n" + reset_state)
        save_state(wins, board)
    else:
        # No win: increment days counter.
        wins['DAYS'] += 1
        # Update the record if current battle days exceed it.
        if wins['DAYS'] > wins['RECORD']:
            wins['RECORD'] = wins['DAYS']
        # Decide move direction: coin toss.
        dice = random.random()
        if dice < 0.5:
            new_boundary = boundary + 1
        else:
            new_boundary = boundary - 1
        # Clamp new_boundary between -1 and BOARD_COLS - 1.
        new_boundary = max(new_boundary, -1)
        new_boundary = min(new_boundary, BOARD_COLS - 1)
    
        # Update the row: set cell to 'A' if i <= new_boundary, else 'B'.
        for i in range(BOARD_COLS):
            row[i] = 'A' if i <= new_boundary else 'B'
        board[row_index] = row
        ascii_output = generate_ascii_board(board, wins)
        save_state(wins, board)
    
    # Write the ASCII output to the output file.
    with open(OUTPUT_FILE, 'w') as f:
        f.write(ascii_output)
    
    return ascii_output

if __name__ == "__main__":
    result = simulate_battle()
    print(result)
