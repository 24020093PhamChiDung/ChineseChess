import copy
from typing import List, Optional, Tuple

from constants import (
    ROWS, COLS, RED, BLACK, EMPTY, WIN_SCORE, PIECE_VALUES,
    GENERAL, ROOK, CANNON, HORSE, SOLDIER,
)
from board import HORSE_MOVES, ORTHO
from evaluate import evaluate_board, get_piece_score

try:  # thu vien khai cuoc (TV2); neu thieu thi bo qua, chay Alpha-Beta thuan
    from opening_book import get_opening_move
except ImportError:  # pragma: no cover
    def get_opening_move(board):
        return None

Pos = Tuple[int, int]
Move = Tuple[Pos, Pos]

INF = float("inf")
DEFAULT_DEPTH = 3
DEFAULT_Q_DEPTH = 2
REPEAT_PENALTY = 50            # phat nuoc di dua ve the co da xuat hien (chong di qua di lai)
CAPTURE_BASE = 10_000_000      # dam bao nuoc an quan luon xep truoc nuoc thuong


# --------------------------------------------------------------------------- #
# KIEM TRA CHIEU NHANH (tuong tu board.is_in_check nhung quet nguoc tu vi tri Tuong)
# --------------------------------------------------------------------------- #
def _in_check(board, player: int) -> bool:
   
    g = board.grid
    pos = board.find_general(player)
    if pos is None:
        return True
    kr, kc = pos
    enemy = -player

    # 4 huong thang: Xe, Tuong doi mat (huong doc), Phao (qua 1 ngoi)
    for dr, dc in ORTHO:
        r, c = kr + dr, kc + dc
        screen_found = False
        while 0 <= r < ROWS and 0 <= c < COLS:
            p = g[r][c]
            if p != EMPTY:
                if not screen_found:
                    if p == enemy * ROOK:
                        return True
                    if p == enemy * GENERAL and dc == 0:   # lo mat tuong
                        return True
                    screen_found = True                    # quan nay lam ngoi
                else:
                    if p == enemy * CANNON:
                        return True
                    break
            r += dr
            c += dc

    # Ma: tim o ma dich co the nhay vao Tuong (chan ma phai trong)
    for (lr, lc), jumps in HORSE_MOVES:
        for jr, jc in jumps:
            hr, hc = kr - jr, kc - jc
            if 0 <= hr < ROWS and 0 <= hc < COLS and g[hr][hc] == enemy * HORSE:
                leg_r, leg_c = hr + lr, hc + lc
                if g[leg_r][leg_c] == EMPTY:
                    return True

    # Tot dich: tien thang vao Tuong, hoac di ngang neu da qua song
    fwd = 1 if enemy == BLACK else -1
    sr = kr - fwd
    if 0 <= sr < ROWS and g[sr][kc] == enemy * SOLDIER:
        return True
    for sc in (kc - 1, kc + 1):
        if 0 <= sc < COLS and g[kr][sc] == enemy * SOLDIER:
            crossed = kr >= 5 if enemy == BLACK else kr <= 4
            if crossed:
                return True
    return False


def _pseudo_moves(board, player: int, captures_only: bool = False) -> List[Move]:
   
    g = board.grid
    gen = board.get_pseudo_legal_moves
    moves: List[Move] = []
    for r in range(ROWS):
        row = g[r]
        for c in range(COLS):
            if row[c] * player > 0:
                if captures_only:
                    for mv in gen(r, c):
                        if g[mv[1][0]][mv[1][1]] != EMPTY:
                            moves.append(mv)
                else:
                    moves.extend(gen(r, c))
    return moves


def _legal_moves(board, player: int, captures_only: bool = False) -> List[Move]:
   
    g = board.grid
    legal: List[Move] = []
    for r in range(ROWS):
        row = g[r]
        for c in range(COLS):
            if row[c] * player > 0:
                for mv in board.get_pseudo_legal_moves(r, c):
                    (_, _), (r2, c2) = mv
                    if captures_only and g[r2][c2] == EMPTY:
                        continue
                    board.make_move(mv)
                    ok = not _in_check(board, player)
                    board.undo_move()
                    if ok:
                        legal.append(mv)
    return legal


# --------------------------------------------------------------------------- #
# 1. SAP XEP NUOC DI (MVV-LVA)
# --------------------------------------------------------------------------- #
def order_moves(board, moves: List[Move]) -> List[Move]:
   
    g = board.grid

    def score(mv: Move) -> int:
        (r1, c1), (r2, c2) = mv
        piece = g[r1][c1]
        victim = g[r2][c2]
        if victim != EMPTY:
            return (CAPTURE_BASE + 10 * PIECE_VALUES[abs(victim)]
                    - PIECE_VALUES[abs(piece)])
        return get_piece_score(piece, r2, c2) - get_piece_score(piece, r1, c1)

    return sorted(moves, key=score, reverse=True)


# --------------------------------------------------------------------------- #
# 2. QUIESCENCE SEARCH
# --------------------------------------------------------------------------- #
def quiescence_search(board, alpha: float, beta: float, is_maximizing: bool,
                      ai_player: int, q_depth: int = DEFAULT_Q_DEPTH,
                      counter: Optional[List[int]] = None) -> float:
   
    if counter is not None:
        counter[0] += 1

    stand_pat = evaluate_board(board, ai_player)
    if q_depth <= 0:
        return stand_pat

    side = ai_player if is_maximizing else -ai_player
    captures = _pseudo_moves(board, side, captures_only=True)
    if not captures:
        return stand_pat
    captures = order_moves(board, captures)

    if is_maximizing:
        best = stand_pat
        if best >= beta:
            return best
        alpha = max(alpha, best)
        for mv in captures:
            board.make_move(mv)
            if _in_check(board, side):          # nuoc tu sat Tuong -> bo
                board.undo_move()
                continue
            val = quiescence_search(board, alpha, beta, False, ai_player, q_depth - 1, counter)
            board.undo_move()
            if val > best:
                best = val
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best

    best = stand_pat
    if best <= alpha:
        return best
    beta = min(beta, best)
    for mv in captures:
        board.make_move(mv)
        if _in_check(board, side):
            board.undo_move()
            continue
        val = quiescence_search(board, alpha, beta, True, ai_player, q_depth - 1, counter)
        board.undo_move()
        if val < best:
            best = val
        beta = min(beta, best)
        if alpha >= beta:
            break
    return best


# --------------------------------------------------------------------------- #
# 3. ALPHA-BETA
# --------------------------------------------------------------------------- #
def alpha_beta(board, depth: int, alpha: float, beta: float, is_maximizing: bool,
               ai_player: int, counter: List[int],
               q_depth: int = DEFAULT_Q_DEPTH) -> float:
   
    counter[0] += 1

    if depth <= 0:
        # quiescence tu dem node cua no -> tru 1 de node nay khong bi dem 2 lan
        counter[0] -= 1
        return quiescence_search(board, alpha, beta, is_maximizing, ai_player,
                                 q_depth, counter)

    side = ai_player if is_maximizing else -ai_player
    moves = order_moves(board, _pseudo_moves(board, side))
    has_legal = False

    if is_maximizing:
        value = -INF
        for mv in moves:
            board.make_move(mv)
            if _in_check(board, side):          # nuoc tu sat Tuong -> bo
                board.undo_move()
                continue
            has_legal = True
            value = max(value, alpha_beta(board, depth - 1, alpha, beta, False,
                                          ai_player, counter, q_depth))
            board.undo_move()
            alpha = max(alpha, value)
            if alpha >= beta:          # cat tia beta
                break
        return value if has_legal else -WIN_SCORE - depth

    value = INF
    for mv in moves:
        board.make_move(mv)
        if _in_check(board, side):
            board.undo_move()
            continue
        has_legal = True
        value = min(value, alpha_beta(board, depth - 1, alpha, beta, True,
                                      ai_player, counter, q_depth))
        board.undo_move()
        beta = min(beta, value)
        if alpha >= beta:              # cat tia alpha
            break
    return value if has_legal else WIN_SCORE + depth


# --------------------------------------------------------------------------- #
# 4. HAM GIAO TIEP CHINH CHO GUI
# --------------------------------------------------------------------------- #
def _position_key(board):
    return (tuple(tuple(row) for row in board.grid), board.current_player)


def get_best_move(board, depth: int = DEFAULT_DEPTH, player: Optional[int] = None,
                  q_depth: int = DEFAULT_Q_DEPTH,
                  repeat_penalty: int = REPEAT_PENALTY) -> Tuple[Optional[Move], int]:
   
    if player is None:
        player = board.current_player

    # Tim kiem tren BAN SAO: GUI chay ham nay o thread rieng trong khi thread chinh
    # van ve ban co that, neu thu nuoc truc tiep tren ban that thi quan se nhay lung tung.
    board = copy.deepcopy(board)
    saved_player = board.current_player
    board.current_player = player          # dam bao make_move/undo_move doi luot dung
    try:
        book_move = get_opening_move(board)
        if book_move is not None:
            return book_move, 0

        counter = [1]                      # node goc
        moves = _legal_moves(board, player)
        if not moves:
            return None, counter[0]
        moves = order_moves(board, moves)

        # cac the co da xuat hien trong van (de tranh lap lai khi hai ben di qua di lai)
        seen = set()
        if repeat_penalty:
            replay = copy.deepcopy(board)
            while replay.move_history:
                replay.undo_move()
                seen.add(_position_key(replay))

        best_move = moves[0]
        best_value = -INF
        for mv in moves:
            board.make_move(mv)
            pen = repeat_penalty if (seen and _position_key(board) in seen) else 0
            # gia tri that = value - pen  =>  cua so alpha cua nut con phai doi thanh best + pen
            child_alpha = best_value + pen if best_value > -INF else -INF
            value = alpha_beta(board, depth - 1, child_alpha, INF, False,
                               player, counter, q_depth) - pen
            board.undo_move()
            if value > best_value:         # '>' : giu nuoc xep truoc khi bang diem
                best_value = value
                best_move = mv
        return best_move, counter[0]
    finally:
        board.current_player = saved_player