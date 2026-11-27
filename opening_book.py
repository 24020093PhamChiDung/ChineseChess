"""opening_book.py - Khai cuoc mau"""

import random
from typing import Optional

PHAO_DAU_PHAI   = ((7, 7), (7, 4))   
PHAO_DAU_TRAI   = ((7, 1), (7, 4))   
PHI_TUONG_TRAI  = ((9, 2), (7, 4))   
PHI_TUONG_PHAI  = ((9, 6), (7, 4))
RED_MA_TRAI     = ((9, 1), (7, 2))
RED_MA_PHAI     = ((9, 7), (7, 6))
RED_TOT3        = ((6, 2), (5, 2))   
RED_TOT7        = ((6, 6), (5, 6))

BLACK_MA_TRAI   = ((0, 1), (2, 2))
BLACK_MA_PHAI   = ((0, 7), (2, 6))
BLACK_PHAO_GIUA = ((2, 1), (2, 4))   
BLACK_PHAO_GIUA2 = ((2, 7), (2, 4))
BLACK_TOT3      = ((3, 2), (4, 2))
BLACK_TOT7      = ((3, 6), (4, 6))

BOOK_MOVES = {
    # --- Đỏ đi nước đầu ---
    (): [PHAO_DAU_PHAI, PHAO_DAU_TRAI, PHI_TUONG_TRAI, RED_MA_TRAI, RED_TOT7],

    # --- Đen đáp lại Pháo đầu: Bình phong mã / pháo đối công ---
    (PHAO_DAU_PHAI,): [BLACK_MA_PHAI, BLACK_MA_TRAI, BLACK_PHAO_GIUA],
    (PHAO_DAU_TRAI,): [BLACK_MA_PHAI, BLACK_MA_TRAI, BLACK_PHAO_GIUA2],

    # --- Đen đáp lại Phi tượng / Mã / Tốt ---
    (PHI_TUONG_TRAI,): [BLACK_MA_PHAI, BLACK_TOT7],
    (RED_MA_TRAI,): [BLACK_MA_PHAI, BLACK_PHAO_GIUA2],
    (RED_TOT7,): [BLACK_PHAO_GIUA, BLACK_MA_TRAI],

    # --- Đỏ nước thứ 2 (sau Pháo đầu + Bình phong mã) ---
    (PHAO_DAU_PHAI, BLACK_MA_PHAI): [RED_MA_TRAI],
    (PHAO_DAU_PHAI, BLACK_MA_TRAI): [RED_MA_TRAI],
    (PHAO_DAU_TRAI, BLACK_MA_PHAI): [RED_MA_PHAI],
    (PHAO_DAU_PHAI, BLACK_PHAO_GIUA): [RED_MA_TRAI],

    # --- Đen nước thứ 2 (hoàn thiện Bình phong mã) ---
    (PHAO_DAU_PHAI, BLACK_MA_PHAI, RED_MA_TRAI): [BLACK_MA_TRAI],
    (PHAO_DAU_PHAI, BLACK_MA_TRAI, RED_MA_TRAI): [BLACK_MA_PHAI],
    (PHAO_DAU_TRAI, BLACK_MA_PHAI, RED_MA_PHAI): [BLACK_MA_TRAI],
}

MAX_BOOK_PLIES = 4

def get_opening_move(board) -> Optional[tuple]:
    """Trả về nước khai cuộc hợp lệ hoặc None để chuyển sang Alpha-Beta."""
    if len(board.move_history) >= MAX_BOOK_PLIES:
        return None

    key = tuple(board.get_move_sequence())
    candidates = BOOK_MOVES.get(key)
    if not candidates:
        return None
    legal = set(board.get_legal_moves())
    valid = [m for m in candidates if m in legal]
    return random.choice(valid) if valid else None