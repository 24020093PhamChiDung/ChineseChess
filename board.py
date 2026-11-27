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

BACK_RANK = [ROOK, HORSE, ELEPHANT, ADVISOR, GENERAL, ADVISOR, ELEPHANT, HORSE, ROOK]

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

    # sinh nước đi
    def get_pseudo_legal_moves(self, r: int, c: int) -> List[Move]:
        """nước đi theo hình học + luật cản của quân tại (r, c)"""
        return []

    def get_legal_moves(self, player: Optional[int] = None) -> List[Move]:
        """nước đi hợp lệ của player (current_player)"""
        return []

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
        """Lịch sử dạng [((r1,c1),(r2,c2)), ...] - dùng cho opening_book."""
        return [((m[0], m[1]), (m[2], m[3])) for m in self.move_history]

    # chiếu tướng - end
    def is_in_check(self, player: int) -> bool:
        """Tướng của player bị chiếu hoặc lộ mặt tướng. TODO (GĐ2)."""
        return False

    def is_checkmate(self, player: int) -> bool:
        """player hết nước đi hợp lệ -> thua. TODO (GĐ2)."""
        return len(self.get_legal_moves(player)) == 0