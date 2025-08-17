import requests # type: ignore
import random
import copy

# API endpoint URL for your 2048 game server
API_URL = "http://localhost:4000"


# --- 2048 Board Utilities (all done locally in Python) ---


def transpose(board):
    """Transpose the board (swap rows and columns). Useful for up/down moves."""
    return [list(row) for row in zip(*board)]


def reverse(board):
    """Reverse each row of the board (useful for right and down moves)."""
    return [list(reversed(row)) for row in board]


def compress_and_merge_row_left(row):
    """
    Compress the row to the left and merge tiles as per 2048 rules.
    Returns the new row and score gained from merges.
    """
    new_row = [val for val in row if val != 0]  # Remove zeros (compress)
    merged_row = []
    skip = False
    score_gain = 0
    i = 0
    while i < len(new_row):
        # Merge pairs of equal tiles
        if not skip and i + 1 < len(new_row) and new_row[i] == new_row[i+1]:
            merged_val = new_row[i] * 2
            merged_row.append(merged_val)
            score_gain += merged_val
            skip = True  # Skip next tile since merged
            i += 2
        else:
            merged_row.append(new_row[i])
            skip = False
            i += 1
    # Fill remaining spaces with zeros
    merged_row += [0] * (len(row) - len(merged_row))
    return merged_row, score_gain


def move_local(board, direction):
    """
    Simulates a move on a local copy of the board in the given direction.
    Returns (new_board, score_gained, moved_flag).
    `moved_flag` indicates whether the move changed the board.
    """
    temp_board = copy.deepcopy(board)
    score_gain = 0
    moved = False

    if direction == "left":
        new_board = []
        for row in temp_board:
            merged_row, gain = compress_and_merge_row_left(row)
            score_gain += gain
            if merged_row != row:
                moved = True
            new_board.append(merged_row)
    elif direction == "right":
        new_board = []
        for row in temp_board:
            rev_row = list(reversed(row))
            merged_row, gain = compress_and_merge_row_left(rev_row)
            merged_row = list(reversed(merged_row))
            score_gain += gain
            if merged_row != row:
                moved = True
            new_board.append(merged_row)
    elif direction == "up":
        temp_board = transpose(temp_board)
        new_board = []
        for row in temp_board:
            merged_row, gain = compress_and_merge_row_left(row)
            score_gain += gain
            if merged_row != row:
                moved = True
            new_board.append(merged_row)
        new_board = transpose(new_board)
    elif direction == "down":
        temp_board = transpose(temp_board)
        new_board = []
        for row in temp_board:
            rev_row = list(reversed(row))
            merged_row, gain = compress_and_merge_row_left(rev_row)
            merged_row = list(reversed(merged_row))
            score_gain += gain
            if merged_row != row:
                moved = True
            new_board.append(merged_row)
        new_board = transpose(new_board)
    else:
        raise ValueError("Invalid direction")

    return new_board, score_gain, moved


def score_board(board):
    """
    Evaluates the board state with a heuristic:
    - Rewards highest tile value.
    - Rewards number of empty tiles.
    - Bonus if highest tile is in bottom-right corner.
    - Bonus for monotonic decreasing sequence in last row.
    """
    highest_tile = max(max(row) for row in board)
    empty_tiles = sum(cell == 0 for row in board for cell in row)
    corner_bonus = 100 if board[3][3] == highest_tile else 0
    mono_bonus = 0
    last_row = board[3]
    if all(last_row[i] >= last_row[i+1] for i in range(3)):
        mono_bonus = 50
    return highest_tile + corner_bonus + empty_tiles * 2 + mono_bonus


def compute_reward(new_state, old_state):
    """
    Computes reward based on change from old_state to new_state:
    - Positive reward for score gain.
    - Bonus if a new highest tile is created.
    - Bonus for empty tiles to encourage board space.
    - Penalty if game over.
    - Small penalty per move to encourage efficiency.
    """
    score_gain = new_state["score"] - old_state["score"]
    highest_tile_bonus = 0
    if new_state["highest"] > old_state["highest"]:
        highest_tile_bonus = 100 * (new_state["highest"] // 128)
    empty_tiles = sum(cell == 0 for row in new_state["board"] for cell in row)
    empty_bonus = empty_tiles * 2
    loss_penalty = -500 if new_state.get("gameOver", False) else 0
    move_penalty = -1
    reward = score_gain + highest_tile_bonus + empty_bonus + loss_penalty + move_penalty
    return reward


def get_highest_tile_position(board):
    """
    Returns the position (row, col) and value of the highest tile on the board.
    """
    highest = -1
    pos = (0, 0)
    for r in range(4):
        for c in range(4):
            if board[r][c] > highest:
                highest = board[r][c]
                pos = (r, c)
    return pos, highest


def lookahead_score(board, depth):
    """
    Recursively performs lookahead to a specified depth.
    Returns the best achievable heuristic board score from this state.
    """
    if depth == 0:
        return score_board(board)

    possible_moves = ["up", "down", "left", "right"]
    max_score = -float('inf')

    for move in possible_moves:
        new_board, _, moved = move_local(board, move)
        if not moved:
            continue
        score = lookahead_score(new_board, depth - 1)
        if score > max_score:
            max_score = score

    if max_score == -float('inf'):
        return -10000  # Heavy penalty if no moves possible (game over)

    return max_score


class RL2048Agent:
    """
    Reinforcement Learning agent for 2048 with heuristic scoring and lookahead.
    """

    def __init__(self):
        self.experience = []

    def reset_game(self):
        """Resets 2048 game on server."""
        requests.post(f"{API_URL}/reset")

    def get_state(self):
        """Fetches current game state from server."""
        resp = requests.get(f"{API_URL}/state")
        return resp.json()

    def send_move(self, direction):
        """Sends move command (up/down/left/right) to server and returns new game state."""
        resp = requests.post(f"{API_URL}/move", json={"direction": direction})
        return resp.json()

    def decide_action(self, state):
        """
        Chooses best move by simulating all moves, evaluating future states
        up to 3 moves ahead (current move + 2 lookahead).
        """
        board = state["board"]
        possible_moves = ["up", "down", "left", "right"]
        best_move = None
        best_score = -float("inf")

        for move in possible_moves:
            new_board, _, moved = move_local(board, move)
            if not moved:
                continue
            score = lookahead_score(new_board, 2)
            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            best_move = random.choice(possible_moves)

        return best_move

    def play_one_game(self):
        """Plays a full game until over, collecting experience tuples."""
        self.reset_game()
        state = self.get_state()
        done = False
        move_count = 0
        game_experience = []

        while not done:
            action = self.decide_action(state)
            old_state = state
            new_state = self.send_move(action)
            reward = compute_reward(new_state, old_state)
            game_experience.append((old_state, action, reward))
            state = new_state
            done = new_state.get("gameOver", False)
            move_count += 1

        print(f"Game over! Moves: {move_count}, Score: {state['score']}, Highest tile: {state['highest']}")
        return game_experience

    def train(self, games=50):
        """Plays multiple games and gathers experience."""
        all_experience = []
        for i in range(games):
            print(f"Playing game {i + 1}/{games}")
            game_exp = self.play_one_game()
            if game_exp:
                final_state = game_exp[-1][0]
                print(f"Game {i + 1}: Highest tile: {final_state['highest']}, Final score: {final_state['score']}")
            else:
                print(f"Game {i + 1}: No experience recorded.")
            all_experience.extend(game_exp)
        print(f"Played {games} games, collected {len(all_experience)} experiences.")


if __name__ == "__main__":
    agent = RL2048Agent()
    agent.train(games=50)
