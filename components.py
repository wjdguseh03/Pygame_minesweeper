"""
Core game logic for Minesweeper.

This module contains pure domain logic without any pygame or pixel-level
concerns. It defines:
- CellState: the state of a single cell
- Cell: a cell positioned by (col,row) with an attached CellState
- Board: grid management, mine placement, adjacency computation, reveal/flag

The Board exposes imperative methods that the presentation layer (run.py)
can call in response to user inputs, and does not know anything about
rendering, timing, or input devices.
"""

import random
from typing import List, Tuple


class CellState:
    """Mutable state of a single cell.

    Attributes:
        is_mine: Whether this cell contains a mine.
        is_revealed: Whether the cell has been revealed to the player.
        is_flagged: Whether the player flagged this cell as a mine.
        adjacent: Number of adjacent mines in the 8 neighboring cells.
    """

    def __init__(self, is_mine: bool = False, is_revealed: bool = False, is_flagged: bool = False, adjacent: int = 0):
        self.is_mine = is_mine
        self.is_revealed = is_revealed
        self.is_flagged = is_flagged
        self.adjacent = adjacent


class Cell:
    """Logical cell positioned on the board by column and row."""

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.state = CellState()


class Board:
    """Minesweeper board state and rules.

    Responsibilities:
    - Generate and place mines with first-click safety
    - Compute adjacency counts for every cell
    - Reveal cells (iterative flood fill when adjacent == 0)
    - Toggle flags, check win/lose conditions
    """

    def __init__(self, cols: int, rows: int, mines: int):
        self.cols = cols
        self.rows = rows
        self.num_mines = mines
        self.cells: List[Cell] = [Cell(c, r) for r in range(rows) for c in range(cols)]
        self._mines_placed = False
        self.revealed_count = 0
        self.game_over = False
        self.win = False

    def index(self, col: int, row: int) -> int:
        """Return the flat list index for (col,row)."""
        return row * self.cols + col

    def is_inbounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

    def neighbors(self, col: int, row: int) -> List[Tuple[int, int]]:
        deltas = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),            (1, 0),
            (-1, 1),  (0, 1),  (1, 1)
        ]
        
        result = []
        for dc, dr in deltas:
            nc, nr = col + dc, row + dr
            if self.is_inbounds(nc, nr):
                result.append((nc, nr))
        
        return result

    def place_mines(self, safe_col: int, safe_row: int) -> None:
        # 1. 전체 좌표 생성
        all_positions = [(c, r) for r in range(self.rows) for c in range(self.cols)]
    
        # 2. 안전지대: 첫 클릭 + 주변
        forbidden = {(safe_col, safe_row)} | set(self.neighbors(safe_col, safe_row))
    
        # 3. 배치 가능한 위치만 필터
        pool = [pos for pos in all_positions if pos not in forbidden]
        random.shuffle(pool)
    
        # 4. 지뢰 배치
        for c, r in pool[:self.num_mines]:
            self.cells[self.index(c, r)].state.is_mine = True
    
        # 5. 각 셀 주변 지뢰 개수 계산
        for cell in self.cells:
            if not cell.state.is_mine:
                count = sum(1 for nc, nr in self.neighbors(cell.col, cell.row)
                            if self.cells[self.index(nc, nr)].state.is_mine)
                cell.state.adjacent = count
    
        # 6. 지뢰 배치 완료 표시
        self._mines_placed = True

    def reveal(self, col: int, row: int) -> None:
        # 1) 범위 밖
        if not self.is_inbounds(col, row):
            return

        cell = self.cells[self.index(col, row)]

        # 2) 이미 오픈/깃발이면 무시
        if cell.state.is_revealed or cell.state.is_flagged:
            return

        # 3) 첫 클릭이면 지뢰 배치
        if not self._mines_placed:
            self.place_mines(col, row)

        # 4) 지뢰를 연 경우 → 게임오버
        if cell.state.is_mine:
            cell.state.is_revealed = True
            self.game_over = True
            self._reveal_all_mines()
            return

        # 5) 숫자 칸 또는 빈 칸 열기
        # BFS/스택 flood fill (반복형)
        stack = [(col, row)]
        while stack:
            c, r = stack.pop()
            cur = self.cells[self.index(c, r)]

            if cur.state.is_revealed:
                continue

            cur.state.is_revealed = True
            self.revealed_count += 1

            # 빈칸(0)인 경우 주변 확장
            if cur.state.adjacent == 0:
                for (nc, nr) in self.neighbors(c, r):
                    nbr = self.cells[self.index(nc, nr)]
                    if not nbr.state.is_revealed and not nbr.state.is_flagged:
                        stack.append((nc, nr))

        # 6) 승리 체크
        self._check_win()

    def toggle_flag(self, col: int, row: int) -> None:
        # Toggle a flag on a non-revealed cell.
        if not self.is_inbounds(col, row):
            return
        # Do not allow flagging after game end or if cell is already revealed
        if self.game_over or self.win:
            return
        cell = self.cells[self.index(col, row)]
        if cell.state.is_revealed:
            return
        cell.state.is_flagged = not cell.state.is_flagged

    def flagged_count(self) -> int:
        # TODO: Return current number of flagged cells.
        pass

    def _reveal_all_mines(self) -> None:
        """Reveal all mines; called on game over."""
        for cell in self.cells:
            if cell.state.is_mine:
                cell.state.is_revealed = True

    def _check_win(self) -> None:
        """Set win=True when all non-mine cells have been revealed."""
        total_cells = self.cols * self.rows
        if self.revealed_count == total_cells - self.num_mines and not self.game_over:
            self.win = True
            for cell in self.cells:
                if not cell.state.is_revealed and not cell.state.is_mine:
                    cell.state.is_revealed = True
