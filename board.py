"""board.py - khung
Quy ước:
grid[r][c], r = 0..9, c = 0..8
Nước đi: ((r1, c1), (r2, c2))
move_history lưu các bộ (r1, c1, r2, c2, captured_piece)
"""
from typing import List, Optional, Tuple

from constants import (
    ROWS, COLS, RED, BLACK, EMPTY,
    GENERAL, ADVISOR, ELEPHANT, ROOK, CANNON, HORSE, SOLDIER,
)

Pos = Tuple[int, int]
Move = Tuple[Pos, Pos]

ORTHO = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAG = ((-1, -1), (-1, 1), (1, -1), (1, 1))
# hướng chân mã, các bước nhảy tương ứng
HORSE_MOVES = (
    ((-1, 0), ((-2, -1), (-2, 1))),
    ((1, 0), ((2, -1), (2, 1))),
    ((0, -1), ((-1, -2), (1, -2))),
    ((0, 1), ((-1, 2), (1, 2))),
)
BACK_RANK = [ROOK, HORSE, ELEPHANT, ADVISOR, GENERAL, ADVISOR, ELEPHANT, HORSE, ROOK]

def side_of(piece):
    if piece > 0:
        return RED
    if piece < 0:
        return BLACK
    return EMPTY

class Board:
    def __init__(self) -> None:
        self.grid: List[List[int]] = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player: int = RED
        self.move_history: List[Tuple[int, int, int, int, int]] = []
        self.reset()

    def reset(self) -> None:
        """Đặt 32 quân vào vị trí chuẩn, Đỏ đi trước, xóa lịch sử."""
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        for c, kind in enumerate(BACK_RANK):
            self.grid[0][c] = -kind
            self.grid[9][c] = kind
        for c in (1, 7):
            self.grid[2][c] = -CANNON
            self.grid[7][c] = CANNON
        for c in (0, 2, 4, 6, 8):
            self.grid[3][c] = -SOLDIER
            self.grid[6][c] = SOLDIER
        self.current_player = RED
        self.move_history = []

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < ROWS and 0 <= c < COLS

    def clear(self):
        # clear bàn cờ
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self.move_history = []

    @staticmethod
    def in_palace(player, r, c):
        if not 3 <= c <= 5:
            return False
        return 7 <= r <= 9 if player == RED else 0 <= r <= 2
    
    # sinh nước đi
    def get_pseudo_legal_moves(self, r, c):
        g = self.grid
        piece = g[r][c]
        if piece == EMPTY:
            return []
        player = side_of(piece)
        kind = abs(piece)
        src = (r, c)
        moves = []

        if kind == ROOK:
            for dr, dc in ORTHO:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc):
                    t = g[nr][nc]
                    if t == EMPTY:
                        moves.append((src, (nr, nc)))
                    else:
                        if t * player < 0:
                            moves.append((src, (nr, nc)))
                        break
                    nr += dr
                    nc += dc

        elif kind == CANNON:
            for dr, dc in ORTHO:
                nr, nc = r + dr, c + dc
                # đi như xe, dừng khi gặp quân đầu tiên (ngòi)
                while self.in_bounds(nr, nc) and g[nr][nc] == EMPTY:
                    moves.append((src, (nr, nc)))
                    nr += dr
                    nc += dc
                # qua ngòi, tìm quân kế tiếp để ăn
                nr += dr
                nc += dc
                while self.in_bounds(nr, nc):
                    t = g[nr][nc]
                    if t != EMPTY:
                        if t * player < 0:
                            moves.append((src, (nr, nc)))
                        break
                    nr += dr
                    nc += dc

        elif kind == HORSE:
            for (lr, lc), jumps in HORSE_MOVES:
                leg_r, leg_c = r + lr, c + lc
                if not self.in_bounds(leg_r, leg_c) or g[leg_r][leg_c] != EMPTY:
                    continue  # bị cản chân mã
                for jr, jc in jumps:
                    nr, nc = r + jr, c + jc
                    if self.in_bounds(nr, nc) and g[nr][nc] * player <= 0:
                        moves.append((src, (nr, nc)))

        elif kind == ELEPHANT:
            for dr, dc in DIAG:
                eye_r, eye_c = r + dr, c + dc
                nr, nc = r + 2 * dr, c + 2 * dc
                if not self.in_bounds(nr, nc) or g[eye_r][eye_c] != EMPTY:
                    continue  # bị cản mắt tượng
                if player == RED and nr < 5:
                    continue  # không được qua sông
                if player == BLACK and nr > 4:
                    continue
                if g[nr][nc] * player <= 0:
                    moves.append((src, (nr, nc)))

        elif kind == ADVISOR:
            for dr, dc in DIAG:
                nr, nc = r + dr, c + dc
                if self.in_palace(player, nr, nc) and g[nr][nc] * player <= 0:
                    moves.append((src, (nr, nc)))

        elif kind == GENERAL:
            for dr, dc in ORTHO:
                nr, nc = r + dr, c + dc
                if self.in_palace(player, nr, nc) and g[nr][nc] * player <= 0:
                    moves.append((src, (nr, nc)))

        elif kind == SOLDIER:
            forward = -1 if player == RED else 1
            crossed = r <= 4 if player == RED else r >= 5
            steps = [(forward, 0)]
            if crossed:
                steps += [(0, -1), (0, 1)]
            for dr, dc in steps:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and g[nr][nc] * player <= 0:
                    moves.append((src, (nr, nc)))

        return moves


    # thực hiện nước đi
    def make_move(self, move: Move) -> None:
        (r1, c1), (r2, c2) = move
        captured = self.grid[r2][c2]
        self.grid[r2][c2] = self.grid[r1][c1]
        self.grid[r1][c1] = EMPTY
        self.move_history.append((r1, c1, r2, c2, captured))
        self.current_player = -self.current_player

    # undo nước đi
    def undo_move(self) -> Optional[Move]:
        if not self.move_history:
            return None
        r1, c1, r2, c2, captured = self.move_history.pop()
        self.grid[r1][c1] = self.grid[r2][c2]
        self.grid[r2][c2] = captured
        self.current_player = -self.current_player
        return ((r1, c1), (r2, c2))

    def get_move_sequence(self) -> List[Move]:
        # lịch sử dạng [((r1,c1),(r2,c2)), ...] cho opening_book
        return [((m[0], m[1]), (m[2], m[3])) for m in self.move_history]

    # chiếu tướng - end
    def find_general(self, player):
        rows = range(7, 10) if player == RED else range(0, 3)
        target = GENERAL * player
        for r in rows:
            for c in range(3, 6):
                if self.grid[r][c] == target:
                    return (r, c)
        return None
    
    def is_in_check(self, player: int) -> bool:
        """chiếu tướng"""
        pos = self.find_general(player)
        if pos is None:
            return True  # tướng bị ăn
        gr, gc = pos

        # lộ mặt tướng
        other = self.find_general(-player)
        if other is not None and other[1] == gc:
            lo, hi = sorted((gr, other[0]))
            if all(self.grid[r][gc] == EMPTY for r in range(lo + 1, hi)):
                return True

        # tướng bị quân team kia chiếu
        for r in range(ROWS):
            for c in range(COLS):
                p = self.grid[r][c]
                if p * player < 0 and abs(p) != GENERAL:
                    for _, dst in self.get_pseudo_legal_moves(r, c):
                        if dst == pos:
                            return True
        return False

    def get_legal_moves(self, player=None):
        # nước đi hợp lệ
        if player is None:
            player = self.current_player
        legal = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] * player > 0:
                    for move in self.get_pseudo_legal_moves(r, c):
                        self.make_move(move)
                        if not self.is_in_check(player):
                            legal.append(move)
                        self.undo_move()
        return legal


    def is_checkmate(self, player: int) -> bool:
        """hết nước đi ->thua"""
        return len(self.get_legal_moves(player)) == 0
    
    def __str__(self):
        sym = {GENERAL: "G", ADVISOR: "A", ELEPHANT: "E", ROOK: "R",
               CANNON: "C", HORSE: "H", SOLDIER: "S"}
        lines = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                p = self.grid[r][c]
                row.append("." if p == EMPTY else (sym[abs(p)] if p > 0 else sym[abs(p)].lower()))
            lines.append(" ".join(row))
        return "\n".join(lines)