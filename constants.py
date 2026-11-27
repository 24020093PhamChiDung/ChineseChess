# kích thước bàn cờ
ROWS = 10
COLS = 9

RED = 1      # đỏ đi trc (ở dưới)
BLACK = -1   # đen đi sau (ở trên)
EMPTY = 0

# mã quân cờ (đỏ là +, đen -)
GENERAL = 1   # Tướng
ADVISOR = 2   # Sĩ
ELEPHANT = 3  # Tượng
ROOK = 4      # Xe
CANNON = 5    # Pháo
HORSE = 6     # Mã
SOLDIER = 7   # Tốt

PIECE_NAMES = {
    GENERAL: "TƯỚNG",
    ADVISOR: "SĨ",
    ELEPHANT: "TƯỢNG",
    ROOK: "XE",
    CANNON: "PHÁO",
    HORSE: "MÃ",
    SOLDIER: "TỐT",
}

# điểm của từng quân cờ
PIECE_VALUES = {
    GENERAL: 100000,
    ROOK: 900,
    CANNON: 450,
    HORSE: 400,
    ELEPHANT: 200,
    ADVISOR: 200,
    SOLDIER: 100,
}

# điểm thắng (alpha-beta)
WIN_SCORE = 1_000_000

# màu giao diện
COLOR_BOARD_BG = (222, 184, 135)
COLOR_LINE = (60, 40, 20)
COLOR_RED_PIECE = (200, 30, 30)
COLOR_BLACK_PIECE = (30, 30, 30)
COLOR_PIECE_BG = (250, 235, 200)
COLOR_SELECT = (255, 215, 0)
COLOR_HINT = (50, 160, 50)
COLOR_LAST_MOVE = (30, 120, 220)