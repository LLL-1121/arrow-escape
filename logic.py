"""Grid rules for 一箭又一箭. Coordinates are (row, column)."""

from functools import lru_cache

SIZE = 6
DIRECTIONS = {"↑": (-1, 0), "↓": (1, 0), "←": (0, -1), "→": (0, 1)}

# Each level is a list of (row, column, direction). All three have a solution.
LEVELS = (
    ((0, 0, "→"), (0, 4, "↑"), (2, 2, "↓"), (4, 2, "←"), (5, 5, "→")),
    ((0, 1, "↓"), (0, 5, "←"), (1, 3, "→"), (2, 1, "→"),
     (3, 5, "↓"), (4, 3, "←"), (5, 0, "↑")),
    ((0, 0, "↓"), (0, 3, "→"), (1, 5, "←"), (2, 0, "→"),
     (2, 3, "↓"), (3, 2, "→"), (4, 5, "↑"), (5, 2, "←"),
     (5, 4, "→")),
)


def blocker(arrows, arrow, size=SIZE):
    """Return the first arrow ahead, or None if the selected arrow can leave."""
    row, col, direction = arrow
    dr, dc = DIRECTIONS[direction]
    occupied = {(r, c): item for item in arrows for r, c, _ in (item,)}
    row += dr
    col += dc
    while 0 <= row < size and 0 <= col < size:
        if (row, col) in occupied:
            return occupied[row, col]
        row += dr
        col += dc
    return None


def solution(level, size=SIZE):
    """Find one valid removal order; used to verify handcrafted levels."""
    @lru_cache(None)
    def search(remaining):
        if not remaining:
            return ()
        for arrow in remaining:
            if blocker(remaining, arrow, size) is None:
                tail = search(tuple(a for a in remaining if a != arrow))
                if tail is not None:
                    return (arrow,) + tail
        return None

    return search(tuple(level))
