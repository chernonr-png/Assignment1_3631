import math
import copy

BOARD_SIZE = 3
EMPTY = 0
WHITE_PAWN = 1  
BLACK_PAWN = 2  

def print_board(board):
    symbols = {EMPTY: '.', WHITE_PAWN: 'W', BLACK_PAWN: 'B'}
    print("\n    0   1   2  (Col)")
    print("  +---+---+---+")
    for r in range(BOARD_SIZE):
        row_str = f"{r} | " + " | ".join(symbols[board[r][c]] for c in range(BOARD_SIZE)) + " |"
        print(row_str)
        print("  +---+---+---+")
    print()

def is_valid_move(board, from_pos, to_pos, player):
    from_row, from_col = from_pos
    to_row, to_col = to_pos

    if not (0 <= to_row < BOARD_SIZE and 0 <= to_col < BOARD_SIZE):
        return False
    if board[from_row][from_col] != player:
        return False

    direction = -1 if player == WHITE_PAWN else 1
    row_diff = to_row - from_row
    col_diff = abs(to_col - from_col)

    # เดินหน้าตรง (ช่องเป้าหมายต้องว่างก่อนถึงจะเดินได้)
    if col_diff == 0 and row_diff == direction and board[to_row][to_col] == EMPTY:
        return True

    # กินทแยง (ช่องเป้าหมายต้องมีหมากฝั่งตรงข้ามก่อนถึงจะกินได้)
    opponent = BLACK_PAWN if player == WHITE_PAWN else WHITE_PAWN
    if col_diff == 1 and row_diff == direction and board[to_row][to_col] == opponent:
        return True

    return False

def get_all_valid_moves(board, player):
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                for new_r in range(BOARD_SIZE):
                    for new_c in range(BOARD_SIZE):
                        if is_valid_move(board, (r, c), (new_r, new_c), player):
                            moves.append(((r, c), (new_r, new_c)))
    return moves

def check_game_end(board, current_player):
    for c in range(BOARD_SIZE):
        if board[0][c] == WHITE_PAWN:
            return WHITE_PAWN
        if board[BOARD_SIZE - 1][c] == BLACK_PAWN:
            return BLACK_PAWN

    white_count = sum(row.count(WHITE_PAWN) for row in board)
    black_count = sum(row.count(BLACK_PAWN) for row in board)
    if white_count == 0:
        return BLACK_PAWN
    if black_count == 0:
        return WHITE_PAWN

    moves = get_all_valid_moves(board, current_player)
    if len(moves) == 0:
        return BLACK_PAWN if current_player == WHITE_PAWN else WHITE_PAWN

    return None

def apply_move(board, from_pos, to_pos):
    board[to_pos[0]][to_pos[1]] = board[from_pos[0]][from_pos[1]]
    board[from_pos[0]][from_pos[1]] = EMPTY


# โค้ดส่วนของสมอง AI: Alpha-Beta Pruning

def alpha_beta(board, depth, alpha, beta, is_maximizing, current_player, ai_player):
    winner = check_game_end(board, current_player)
    if winner is not None:
        return (10 - depth) if winner == ai_player else (-10 + depth)

    opponent = BLACK_PAWN if current_player == WHITE_PAWN else WHITE_PAWN
    moves = get_all_valid_moves(board, current_player)

    if is_maximizing:
        max_eval = -math.inf
        for move in moves:
            temp_board = copy.deepcopy(board)
            apply_move(temp_board, move[0], move[1])
            eval_score = alpha_beta(temp_board, depth + 1, alpha, beta, False, opponent, ai_player)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            temp_board = copy.deepcopy(board)
            apply_move(temp_board, move[0], move[1])
            eval_score = alpha_beta(temp_board, depth + 1, alpha, beta, True, opponent, ai_player)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def alpha_beta_player(board, ai_player):
    best_score = -math.inf
    best_move = None
    moves = get_all_valid_moves(board, ai_player)
    
    if not moves:
        return None

    for move in moves:
        temp_board = copy.deepcopy(board)
        apply_move(temp_board, move[0], move[1])
        opponent = BLACK_PAWN if ai_player == WHITE_PAWN else WHITE_PAWN
        score = alpha_beta(temp_board, 0, -math.inf, math.inf, False, opponent, ai_player)
        
        if score > best_score:
            best_score = score
            best_move = move
            
    return best_move

# โค้ดตัวGame Loop หลัก

def play_game():
    board = [
        [BLACK_PAWN, BLACK_PAWN, BLACK_PAWN],
        [EMPTY, EMPTY, EMPTY],
        [WHITE_PAWN, WHITE_PAWN, WHITE_PAWN]
    ]
    current_player = WHITE_PAWN

    print("=== ยินดีต้อนรับสู่เกม Hexapawn vs AlphaBeta AI ===")
    print("คุณคือ: White (W) | AI คือ: Black (B)")

    while True:
        print_board(board)
        
        winner = check_game_end(board, current_player)
        if winner is not None:
            winner_name = "White (You)" if winner == WHITE_PAWN else "Black (AI)"
            print(f" จบเกม! {winner_name} เป็นฝ่ายชนะ!")
            break

        if current_player == WHITE_PAWN:
            print(">> ถึงตาคุณเดินเเล้ว (White) <<")
            valid_moves = get_all_valid_moves(board, WHITE_PAWN)
            
            while True:
                try:
                    user_input = input("กรอกพิกัดที่จะเดิน: ")
                    f_r, f_c, t_r, t_c = map(int, user_input.split())
                    move = ((f_r, f_c), (t_r, t_c))
                    
                    if move in valid_moves:
                        apply_move(board, move[0], move[1])
                        break
                    else:
                        print("❌ ตัวเลขพิกัดไม่ถูกต้อง กรอกเฉพาะตัวเลขพิกัดที่อยู่ในรายการเท่านั้น! ")
                except (ValueError, IndexError):
                    print("❌ รูปแบบไม่ถูกต้อง  ex: 2 1 1 1")
            
            current_player = BLACK_PAWN

        else:
            print(">> ตาของ AI (Black) กำลังคำนวณ... <<")
            ai_move = alpha_beta_player(board, BLACK_PAWN)
            if ai_move:
                print(f" AI เดินจาก {ai_move[0]} ไปที่ {ai_move[1]}")
                apply_move(board, ai_move[0], ai_move[1])
            
            current_player = WHITE_PAWN

if __name__ == "__main__":
    play_game()