import random
import pygame

from constants import (
    ROWS, COLS, RED, BLACK, EMPTY,
    GENERAL, ADVISOR, ELEPHANT, ROOK, CANNON, HORSE, SOLDIER,
    PIECE_NAMES,
)
from board import Board

HANZI_RED = {
    GENERAL: "帥", ADVISOR: "仕", ELEPHANT: "相",
    ROOK: "俥", CANNON: "炮", HORSE: "傌", SOLDIER: "兵",
}
HANZI_BLACK = {
    GENERAL: "將", ADVISOR: "士", ELEPHANT: "象",
    ROOK: "車", CANNON: "包", HORSE: "馬", SOLDIER: "卒",
}

BG_OUTER = (38, 52, 42)
WOOD_BASE = (205, 148, 92)
WOOD_GRAIN = (192, 134, 78)
WOOD_BORDER = (118, 72, 34)
LINE_DARK = (92, 54, 24)
LINE_HIGHLIGHT = (232, 182, 128)
WATERMARK_COLOR = (165, 110, 62)

IVORY_LIGHT = (248, 240, 222)
IVORY_SHADE = (224, 208, 178)
RED_INK = (188, 28, 28)
BLACK_INK = (32, 30, 28)
CORNER_GREEN = (45, 235, 70)
HINT_DOT = (45, 210, 75)
CAPTURE_RING = (235, 55, 55)

CELL_SIZE = 68
BOARD_PAD_X = 48
BOARD_PAD_Y = 58
OUTER_MARGIN = 22
PANEL_HEIGHT = 68
PIECE_RADIUS = 28

BOARD_BOX_W = BOARD_PAD_X * 2 + CELL_SIZE * (COLS - 1)
BOARD_BOX_H = BOARD_PAD_Y * 2 + CELL_SIZE * (ROWS - 1)
WINDOW_W = BOARD_BOX_W + OUTER_MARGIN * 2
WINDOW_H = BOARD_BOX_H + OUTER_MARGIN * 2 + PANEL_HEIGHT


def _load_cjk_font(size: int) -> tuple[pygame.font.Font, bool]:
    candidates = [
        "stkaiti", "kaiti", "dfkaisb", "simsun", "nsimsun",
        "microsoftyahei", "pingfangsc", "hiraginosansgb",
        "notoserifcjksc", "notosanscjksc", "wenquanyizenhei",
    ]
    available = set(pygame.font.get_fonts())
    for name in candidates:
        if name in available:
            return pygame.font.SysFont(name, size, bold=True), True
    return pygame.font.SysFont("arial,dejavusans,tahoma", max(14, size // 2), bold=True), False


class XiangqiApp:
    def __init__(self, ai_depth: int = 3) -> None:
        pygame.init()
        pygame.display.set_caption("Cờ Tướng AI — Minimax & Alpha-Beta Pruning")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        self.font_piece, self.use_hanzi = _load_cjk_font(34)
        self.font_river = pygame.font.SysFont("georgia,timesnewroman,dejavuserif", 28, bold=True, italic=True)
        self.font_coord = pygame.font.SysFont("arial,dejavusans", 15, bold=True)

        self.board_surface = self._build_wood_board_surface()
        self.board = Board()
        self.human_side = RED
        self.ai_side = BLACK
        self.ai_depth = ai_depth

        self.selected_pos = None
        self.valid_targets = []
        self.last_move = None

    def grid_to_pixel(self, r: int, c: int) -> tuple[int, int]:
        x = OUTER_MARGIN + BOARD_PAD_X + c * CELL_SIZE
        y = OUTER_MARGIN + BOARD_PAD_Y + r * CELL_SIZE
        return x, y

    def pixel_to_grid(self, px: int, py: int):
        c = round((px - OUTER_MARGIN - BOARD_PAD_X) / CELL_SIZE)
        r = round((py - OUTER_MARGIN - BOARD_PAD_Y) / CELL_SIZE)
        if not self.board.in_bounds(r, c):
            return None
        gx, gy = self.grid_to_pixel(r, c)
        if (px - gx) ** 2 + (py - gy) ** 2 <= (PIECE_RADIUS + 5) ** 2:
            return (r, c)
        return None

    def _draw_engraved_line(self, surf: pygame.Surface, p1: tuple[int, int], p2: tuple[int, int], width: int = 2) -> None:
        pygame.draw.line(surf, LINE_HIGHLIGHT, (p1[0] + 1, p1[1] + 1), (p2[0] + 1, p2[1] + 1), width)
        pygame.draw.line(surf, LINE_DARK, p1, p2, width)

    def _draw_star_marker(self, surf: pygame.Surface, r: int, c: int) -> None:
        x = BOARD_PAD_X + c * CELL_SIZE
        y = BOARD_PAD_Y + r * CELL_SIZE
        gap, length = 5, 10
        for dx in (-1, 1):
            for dy in (-1, 1):
                if (c == 0 and dx == -1) or (c == COLS - 1 and dx == 1):
                    continue
                sx, sy = x + dx * gap, y + dy * gap
                self._draw_engraved_line(surf, (sx, sy), (sx + dx * length, sy), 2)
                self._draw_engraved_line(surf, (sx, sy), (sx, sy + dy * length), 2)

    def _build_wood_board_surface(self) -> pygame.Surface:
        surf = pygame.Surface((BOARD_BOX_W, BOARD_BOX_H), pygame.SRCALPHA)

        pygame.draw.rect(surf, WOOD_BASE, (0, 0, BOARD_BOX_W, BOARD_BOX_H), border_radius=14)
        rng = random.Random(42)
        for y in range(6, BOARD_BOX_H - 6, 4):
            tone = WOOD_GRAIN if rng.random() < 0.45 else (214, 158, 102)
            pygame.draw.line(surf, tone, (8, y), (BOARD_BOX_W - 8, y), 1)
        pygame.draw.rect(surf, WOOD_BORDER, (0, 0, BOARD_BOX_W, BOARD_BOX_H), 4, border_radius=14)
        pygame.draw.rect(surf, LINE_HIGHLIGHT, (4, 4, BOARD_BOX_W - 8, BOARD_BOX_H - 8), 1, border_radius=11)

        x0, y0 = BOARD_PAD_X, BOARD_PAD_Y
        x1 = BOARD_PAD_X + (COLS - 1) * CELL_SIZE
        y1 = BOARD_PAD_Y + (ROWS - 1) * CELL_SIZE
        y_river_top = BOARD_PAD_Y + 4 * CELL_SIZE
        y_river_bot = BOARD_PAD_Y + 5 * CELL_SIZE

        pygame.draw.rect(surf, LINE_DARK, (x0 - 5, y0 - 5, (x1 - x0) + 10, (y1 - y0) + 10), 2)

        for r in range(ROWS):
            y = BOARD_PAD_Y + r * CELL_SIZE
            self._draw_engraved_line(surf, (x0, y), (x1, y), 2)

        for c in range(COLS):
            x = BOARD_PAD_X + c * CELL_SIZE
            if c == 0 or c == COLS - 1:
                self._draw_engraved_line(surf, (x, y0), (x, y1), 2)
            else:
                self._draw_engraved_line(surf, (x, y0), (x, y_river_top), 2)
                self._draw_engraved_line(surf, (x, y_river_bot), (x, y1), 2)

        for top_r, bot_r in ((0, 2), (7, 9)):
            px1, py1 = BOARD_PAD_X + 3 * CELL_SIZE, BOARD_PAD_Y + top_r * CELL_SIZE
            px2, py2 = BOARD_PAD_X + 5 * CELL_SIZE, BOARD_PAD_Y + bot_r * CELL_SIZE
            self._draw_engraved_line(surf, (px1, py1), (px2, py2), 2)
            self._draw_engraved_line(surf, (px2, py1), (px1, py2), 2)

        for sr, sc in [
            (2, 1), (2, 7), (7, 1), (7, 7),
            (3, 0), (3, 2), (3, 4), (3, 6), (3, 8),
            (6, 0), (6, 2), (6, 4), (6, 6), (6, 8),
        ]:
            self._draw_star_marker(surf, sr, sc)

        river_y = (y_river_top + y_river_bot) // 2
        wm_hi = self.font_river.render("Sở Hà   —   Hán Giới", True, LINE_HIGHLIGHT)
        wm_main = self.font_river.render("Sở Hà   —   Hán Giới", True, WATERMARK_COLOR)
        surf.blit(wm_hi, wm_hi.get_rect(center=(BOARD_BOX_W // 2 + 1, river_y + 1)))
        surf.blit(wm_main, wm_main.get_rect(center=(BOARD_BOX_W // 2, river_y)))

        for c in range(COLS):
            x = BOARD_PAD_X + c * CELL_SIZE
            top_txt = self.font_coord.render(str(c + 1), True, WATERMARK_COLOR)
            bot_txt = self.font_coord.render(str(COLS - c), True, WATERMARK_COLOR)
            surf.blit(top_txt, top_txt.get_rect(center=(x, y0 - 30)))
            surf.blit(bot_txt, bot_txt.get_rect(center=(x, y1 + 30)))

        return surf

    def draw_corner_brackets(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        x, y = self.grid_to_pixel(r, c)
        d = PIECE_RADIUS + 4
        arm = 11
        corners = [
            ((x - d, y - d), (1, 1)),
            ((x + d, y - d), (-1, 1)),
            ((x - d, y + d), (1, -1)),
            ((x + d, y + d), (-1, -1)),
        ]
        for (cx, cy), (dx, dy) in corners:
            pygame.draw.line(self.screen, (20, 60, 25), (cx + 1, cy + 1), (cx + dx * arm + 1, cy + 1), 3)
            pygame.draw.line(self.screen, (20, 60, 25), (cx + 1, cy + 1), (cx + 1, cy + dy * arm + 1), 3)
            pygame.draw.line(self.screen, color, (cx, cy), (cx + dx * arm, cy), 3)
            pygame.draw.line(self.screen, color, (cx, cy), (cx, cy + dy * arm), 3)

    def draw_highlights(self) -> None:
        if self.last_move:
            (r1, c1), (r2, c2) = self.last_move
            self.draw_corner_brackets(r1, c1, CORNER_GREEN)
            self.draw_corner_brackets(r2, c2, CORNER_GREEN)

        if self.selected_pos:
            self.draw_corner_brackets(*self.selected_pos, (255, 230, 60))

        for tr, tc in self.valid_targets:
            x, y = self.grid_to_pixel(tr, tc)
            if self.board.grid[tr][tc] == EMPTY:
                pygame.draw.circle(self.screen, (25, 70, 30), (x + 1, y + 1), 8)
                pygame.draw.circle(self.screen, HINT_DOT, (x, y), 7)
            else:
                pygame.draw.circle(self.screen, CAPTURE_RING, (x, y), PIECE_RADIUS + 4, 3)

    def draw_pieces(self) -> None:
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board.grid[r][c]
                if piece == EMPTY:
                    continue
                x, y = self.grid_to_pixel(r, c)
                ink = RED_INK if piece > 0 else BLACK_INK

                pygame.draw.circle(self.screen, (75, 45, 20), (x + 2, y + 4), PIECE_RADIUS)
                pygame.draw.circle(self.screen, IVORY_SHADE, (x, y), PIECE_RADIUS)
                pygame.draw.circle(self.screen, IVORY_LIGHT, (x, y - 1), PIECE_RADIUS - 2)
                pygame.draw.circle(self.screen, (125, 105, 80), (x, y), PIECE_RADIUS, 2)
                pygame.draw.circle(self.screen, ink, (x, y - 1), PIECE_RADIUS - 5, 2)

                kind = abs(piece)
                if self.use_hanzi:
                    label = HANZI_RED[kind] if piece > 0 else HANZI_BLACK[kind]
                else:
                    label = PIECE_NAMES[kind]

                txt = self.font_piece.render(label, True, ink)
                self.screen.blit(txt, txt.get_rect(center=(x, y - 1)))