"""
Pygame presentation layer for Minesweeper.

This module owns:
- Renderer: all drawing of cells, header, and result overlays
- InputController: translate mouse input to board actions and UI feedback
- Game: orchestration of loop, timing, state transitions, and composition

The logic lives in components.Board; this module should not implement rules.
"""

import sys

import pygame

import config
from components import Board
from pygame.locals import Rect


class Renderer:
    """Draws the Minesweeper UI.

    Knows how to draw individual cells with flags/numbers, header info,
    and end-of-game overlays with a semi-transparent background.
    """

    def __init__(self, screen: pygame.Surface, board: Board):
        self.screen = screen
        self.board = board
        self.font = pygame.font.Font(config.font_name, config.font_size)
        self.header_font = pygame.font.Font(config.font_name, config.header_font_size)
        self.result_font = pygame.font.Font(config.font_name, config.result_font_size)

    def cell_rect(self, col: int, row: int) -> Rect:
        """Return the rectangle in pixels for the given grid cell."""
        x = config.margin_left + col * config.cell_size
        y = config.margin_top + row * config.cell_size
        return Rect(x, y, config.cell_size, config.cell_size)

    def draw_cell(self, col: int, row: int, highlighted: bool) -> None:
        """Draw a single cell, respecting revealed/flagged state and highlight."""
        cell = self.board.cells[self.board.index(col, row)]
        rect = self.cell_rect(col, row)
        if cell.state.is_revealed:
            pygame.draw.rect(self.screen, config.color_cell_revealed, rect)
            if cell.state.is_mine:
                pygame.draw.circle(self.screen, config.color_cell_mine, rect.center, rect.width // 4)
            elif cell.state.adjacent > 0:
                color = config.number_colors.get(cell.state.adjacent, config.color_text)
                label = self.font.render(str(cell.state.adjacent), True, color)
                label_rect = label.get_rect(center=rect.center)
                self.screen.blit(label, label_rect)
        else:
            base_color = config.color_highlight if highlighted else config.color_cell_hidden
            pygame.draw.rect(self.screen, base_color, rect)
            if cell.state.is_flagged:
                flag_w = max(6, rect.width // 3)
                flag_h = max(8, rect.height // 2)
                pole_x = rect.left + rect.width // 3
                pole_y = rect.top + 4
                pygame.draw.line(self.screen, config.color_flag, (pole_x, pole_y), (pole_x, pole_y + flag_h), 2)
                pygame.draw.polygon(
                    self.screen,
                    config.color_flag,
                    [
                        (pole_x + 2, pole_y),
                        (pole_x + 2 + flag_w, pole_y + flag_h // 3),
                        (pole_x + 2, pole_y + flag_h // 2),
                    ],
                )
        pygame.draw.rect(self.screen, config.color_grid, rect, 1)

    def draw_header(self, remaining_mines: int, time_text: str) -> None:
        """Draw the header bar containing remaining mines and elapsed time."""
        pygame.draw.rect(
            self.screen,
            config.color_header,
            Rect(0, 0, config.width, config.margin_top - 4),
        )
        left_text = f"Mines: {remaining_mines}"
        right_text = f"Time: {time_text}"
        left_label = self.header_font.render(left_text, True, config.color_header_text)
        right_label = self.header_font.render(right_text, True, config.color_header_text)
        self.screen.blit(left_label, (10, 12))
        self.screen.blit(right_label, (config.width - right_label.get_width() - 10, 12))

    def draw_result_overlay(self, text: str | None) -> None:
        """Draw a semi-transparent overlay with centered result text, if any."""
        if not text:
            return
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, config.result_overlay_alpha))
        self.screen.blit(overlay, (0, 0))
        label = self.result_font.render(text, True, config.color_result)
        rect = label.get_rect(center=(config.width // 2, config.height // 2))
        self.screen.blit(label, rect)

    def restart_button_rect(self) -> Rect:
    x = (config.width - config.restart_button_width) // 2
    y = (config.height // 2) + 60
    return Rect(x, y, config.restart_button_width, config.restart_button_height)

    def draw_restart_button(self, mouse_pos) -> None:
    rect = self.restart_button_rect()
    hover = rect.collidepoint(mouse_pos)
    color = config.restart_button_hover if hover else config.restart_button_color

    pygame.draw.rect(self.screen, color, rect, border_radius=8)

    label = self.font.render("RESTART", True, config.restart_button_text_color)
    label_rect = label.get_rect(center=rect.center)
    self.screen.blit(label, label_rect)
    def draw_highscore(self, text: str):
    label = self.font.render(text, True, config.color_header_text)
    rect = label.get_rect(center=(config.width // 2, (config.height // 2) + 130))
    self.screen.blit(label, rect)

class InputController:
    """Translates input events into game and board actions."""

    def __init__(self, game: "Game"):
        self.game = game

    def pos_to_grid(self, x: int, y: int):
        """Convert pixel coordinates to (col,row) grid indices or (-1,-1) if out of bounds."""
        if not (config.margin_left <= x < config.width - config.margin_right):
            return -1, -1
        if not (config.margin_top <= y < config.height - config.margin_bottom):
            return -1, -1
        col = (x - config.margin_left) // config.cell_size
        row = (y - config.margin_top) // config.cell_size
        if 0 <= col < self.game.board.cols and 0 <= row < self.game.board.rows:
            return int(col), int(row)
        return -1, -1

    def handle_mouse(self, pos, button) -> None:
        game = self.game
        # 게임 종료 상태
        if game.board.game_over or game.board.win:
            if button == config.mouse_left:
                rect = game.renderer.restart_button_rect()
                if rect.collidepoint(pos):
                    game.reset()
             return


        col, row = self.pos_to_grid(pos[0], pos[1])
        if col == -1:
            return

        game = self.game
        board = game.board

        # 좌클릭 → Reveal
        if button == config.mouse_left:
            game.highlight_targets.clear()

            if not game.started:
                game.started = True
                game.start_ticks_ms = pygame.time.get_ticks()

            board.reveal(col, row)

        # 우클릭 → Flag toggle
        elif button == config.mouse_right:
            game.highlight_targets.clear()
            board.toggle_flag(col, row)

        # 휠클릭 → 주변 하이라이트
        elif button == config.mouse_middle:
            neighbors = board.neighbors(col, row)

            # 이미 열린 셀은 제외
            game.highlight_targets = {
                (nc, nr)
                for (nc, nr) in neighbors
                if not board.cells[board.index(nc, nr)].state.is_revealed
            }

            # 일정 시간(예: 300ms) 동안만 표시
            game.highlight_until_ms = pygame.time.get_ticks() + config.highlight_duration_ms

class Game:
    """Main application object orchestrating loop and high-level state."""

    def __init__(self):
        self.highscore_ms = self._load_highscore()

        pygame.init()
        pygame.display.set_caption(config.title)
        self.screen = pygame.display.set_mode(config.display_dimension)
        self.clock = pygame.time.Clock()

        self.difficulty = config.default_difficulty
        self._init_board_by_difficulty()
        self.hints_left = 3

        self.renderer = Renderer(self.screen, self.board)
        self.input = InputController(self)
        self.highlight_targets = set()
        self.highlight_until_ms = 0
        self.started = False
        self.start_ticks_ms = 0
        self.end_ticks_ms = 0
    def _load_highscore(self):
    try:
        with open(config.highscore_file, "r") as f:
            return int(f.read())
    except:
        return None
    def _save_highscore(self, ms: int):
    with open(config.highscore_file, "w") as f:
        f.write(str(ms))

    def reset(self):
        """Reset the game state and start a new board."""
        self._init_board_by_difficulty()
        self.hints_left = 3

        self.highlight_targets.clear()
        self.highlight_until_ms = 0
        self.started = False
        self.start_ticks_ms = 0
        self.end_ticks_ms = 0

    def _elapsed_ms(self) -> int:
        """Return elapsed time in milliseconds (stops when game ends)."""
        if not self.started:
            return 0
        if self.end_ticks_ms:
            return self.end_ticks_ms - self.start_ticks_ms
        return pygame.time.get_ticks() - self.start_ticks_ms

    def _format_time(self, ms: int) -> str:
        """Format milliseconds as mm:ss string."""
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _result_text(self) -> str | None:
        """Return result label to display, or None if game continues."""
        if self.board.game_over:
            return "GAME OVER"
        if self.board.win:
            return "GAME CLEAR"
        return None

    def draw(self):
        """Render one frame: header, grid, result overlay."""
        if pygame.time.get_ticks() > self.highlight_until_ms and self.highlight_targets:
            self.highlight_targets.clear()
        self.screen.fill(config.color_bg)
        remaining = max(0, config.num_mines - self.board.flagged_count())
        time_text = self._format_time(self._elapsed_ms())
        self.renderer.draw_header(remaining, time_text)
        now = pygame.time.get_ticks()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                highlighted = (now <= self.highlight_until_ms) and ((c, r) in self.highlight_targets)
                self.renderer.draw_cell(c, r, highlighted)
        self.renderer.draw_result_overlay(self._result_text())
        if self._result_text():
            self.renderer.draw_restart_button(pygame.mouse.get_pos())
        result = self._result_text()
        self.renderer.draw_result_overlay(result)

        if result:
            self.renderer.draw_restart_button(pygame.mouse.get_pos())

            if self.highscore_ms is not None:
                hs_text = f"High Score: {self._format_time(self.highscore_ms)}"
                self.renderer.draw_highscore(hs_text)
                
        pygame.display.flip()

    def run_step(self) -> bool:
        """Process inputs, update time, draw, and tick the clock once."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                if event.key == pygame.K_h:
                    self.use_hint()

            # 난이도 선택 (게임 시작 전만 가능)
            if not self.started:
                if event.key == pygame.K_1:
                    self.set_difficulty("EASY")
                elif event.key == pygame.K_2:
                    self.set_difficulty("NORMAL")
                elif event.key == pygame.K_3:
                    self.set_difficulty("HARD")

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input.handle_mouse(event.pos, event.button)
        if (self.board.game_over or self.board.win) and self.started and not self.end_ticks_ms:
            self.end_ticks_ms = pygame.time.get_ticks()

        # 🏆 하이 스코어 갱신 (클리어 시만)
            if self.board.win:
            elapsed = self.end_ticks_ms - self.start_ticks_ms
            if self.highscore_ms is None or elapsed < self.highscore_ms:
                self.highscore_ms = elapsed
                self._save_highscore(elapsed)

            
        self.draw()
        self.clock.tick(config.fps)
        return True
    def _init_board_by_difficulty(self):
    diff = config.difficulties[self.difficulty]
    self.board = Board(diff["cols"], diff["rows"], diff["mines"])
    self.renderer.board = self.board

    def set_difficulty(self, level: str):
    # 게임 시작 후에는 변경 불가
    if self.started:
        return
    if level not in config.difficulties:
        return
    self.difficulty = level
    self.reset()

    def use_hint(self):
    if not self.started or self.board.game_over or self.board.win:
        return
    if self.hints_left <= 0:
        return

    candidates = []
    for r in range(self.board.rows):
        for c in range(self.board.cols):
            cell = self.board.cells[self.board.index(c, r)]
            if not cell.state.is_revealed and not cell.state.is_mine:
                candidates.append((c, r))

    if not candidates:
        return

    import random
    c, r = random.choice(candidates)
    self.board.reveal(c, r)
    self.hints_left -= 1


def main() -> int:
    """Application entrypoint: run the main loop until quit."""
    game = Game()
    running = True
    while running:
        running = game.run_step()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())