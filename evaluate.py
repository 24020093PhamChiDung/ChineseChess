"""evaluate.py : Chấm điểm một thế cờ bất kỳ theo góc nhìn của AI để giúp Alpha-Beta biết nước đi nào đang chiếm ưu thế.
Điểm 1 quân = PIECE_VALUES + điểm vị trí(PST)
Điểm thế cờ = Tổng điểm quân mình - tổng điểm quân đối thủ"""

from constants import ROWS, COLS, PIECE_VALUES
from constants import GENERAL, ADVISOR, ELEPHANT, ROOK, CANNON, HORSE, SOLDIER

# PST: luu ma tran diem thuong cho cac quan. 
# PST viet theo goc nhin quan Do, quan Den dung chung bang cach lat hang (9-r). Moi bang 10 hang x 9 cot
PST = {
    # Tướng: khuyen khich o giua cung, hang day
    GENERAL: [
        [0]*9, [0]*9, [0]*9, [0]*9, [0]*9, [0]*9, [0]*9,
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 5, 8, 5, 0, 0, 0],
    ],

    # Si
    ADVISOR: [
        [0]*9, [0]*9, [0]*9, [0]*9, [0]*9, [0]*9, [0]*9,
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 3, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 2, 0, 0, 0],
    ],

    # Tượng
    ELEPHANT: [
        [0]*9, [0]*9, [0]*9, [0]*9, [0]*9,
        [0, 0, 2, 0, 0, 0, 2, 0, 0],
        [0]*9,
        [2, 0, 0, 0, 3, 0, 0, 0, 2],
        [0]*9,
        [0, 0, 2, 0, 0, 0, 2, 0, 0],
    ],

    # Xe: thưởng hàng thoáng, hàng sát đáy địch, cột giữa; phạt biên đáy nhà
    ROOK: [
        [14, 14, 12, 18, 16, 18, 12, 14, 14],
        [16, 20, 18, 24, 26, 24, 18, 20, 16],
        [12, 12, 12, 18, 18, 18, 12, 12, 12],
        [12, 18, 16, 22, 22, 22, 16, 18, 12],
        [12, 14, 12, 18, 18, 18, 12, 14, 12],
        [12, 16, 14, 20, 20, 20, 14, 16, 12],
        [6, 10, 8, 14, 14, 14, 8, 10, 6],
        [4, 8, 6, 14, 12, 14, 6, 8, 4],
        [8, 4, 8, 16, 8, 16, 8, 4, 8],
        [-2, 10, 6, 14, 12, 14, 6, 10, -2],
    ],

    # Pháo: thưởng cột giữa (pháo đầu) và hàng đáy địch
    CANNON: [
        [6, 4, 0, -10, -12, -10, 0, 4, 6],
        [2, 2, 0, -4, -14, -4, 0, 2, 2],
        [2, 2, 0, -10, -8, -10, 0, 2, 2],
        [0, 0, -2, 4, 10, 4, -2, 0, 0],
        [0, 0, 0, 2, 8, 2, 0, 0, 0],
        [-2, 0, 4, 2, 6, 2, 4, 0, -2],
        [0, 0, 0, 2, 4, 2, 0, 0, 0],
        [4, 0, 8, 6, 10, 6, 8, 0, 4],
        [0, 2, 4, 6, 6, 6, 4, 2, 0],
        [0, 0, 2, 6, 6, 6, 2, 0, 0],
    ],

    # Mã: thưởng trung tâm, phạt biên
    HORSE: [
        [4, 8, 16, 12, 4, 12, 16, 8, 4],
        [4, 10, 28, 16, 8, 16, 28, 10, 4],
        [12, 14, 16, 20, 18, 20, 16, 14, 12],
        [8, 24, 18, 24, 20, 24, 18, 24, 8],
        [6, 16, 14, 18, 16, 18, 14, 16, 6],
        [4, 12, 16, 14, 12, 14, 16, 12, 4],
        [2, 6, 8, 6, 10, 6, 8, 6, 2],
        [4, 2, 8, 8, 4, 8, 8, 2, 4],
        [0, 2, 4, 4, -2, 4, 4, 2, 0],
        [0, -4, 0, 0, 0, 0, 0, -4, 0],
    ],

    # Tốt: chưa qua sông ~0; qua sông tăng dần, áp sát cung địch tăng mạnh
    SOLDIER: [
        [0, 3, 6, 9, 12, 9, 6, 3, 0],
        [18, 36, 56, 80, 120, 80, 56, 36, 18],
        [14, 26, 42, 60, 80, 60, 42, 26, 14],
        [10, 20, 30, 34, 40, 34, 30, 20, 10],
        [6, 12, 18, 18, 20, 18, 18, 12, 6],
        [2, 0, 8, 0, 8, 0, 8, 0, 2],
        [0, 0, -2, 0, 4, 0, -2, 0, 0],
        [0]*9, [0]*9, [0]*9,
    ],
}

def get_piece_score(piece: int, r: int, c: int) -> int:
    kind = abs(piece)
    row_idx = r if piece > 0 else 9 - r  # Đen: lật hàng 9 - r
    return PIECE_VALUES[kind] + PST[kind][row_idx][c]

def evaluate_board(board, curr_player: int) -> int:
    score = 0
    grid = board.grid
    for r in range(ROWS):
        row = grid[r]
        for c in range(COLS):
            p = row[c]
            if p:
                s = get_piece_score(p, r, c)
                score += s if p * curr_player > 0 else -s
    return score