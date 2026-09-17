"""GUI state tests; run where a desktop display is available."""

import unittest
from types import SimpleNamespace

from game import Game, CELL, PAD
from logic import LEVELS, solution


class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.root.withdraw()
        self.game.root.after = lambda _delay, callback, *args: callback(*args)
        self.game.advance()

    def tearDown(self):
        self.game.root.destroy()

    def click(self, arrow):
        row, col, _ = arrow
        self.game.click(SimpleNamespace(x=PAD + col * CELL + CELL // 2,
                                        y=PAD + row * CELL + CELL // 2))

    def test_T01_T02_T03_clear_blocked_edge(self):
        blocked = LEVELS[0][0]
        self.click(blocked)
        self.assertIn(blocked, self.game.arrows)
        self.assertEqual(self.game.misses, 2)
        edge = LEVELS[0][1]
        self.click(edge)
        self.assertNotIn(edge, self.game.arrows)
        self.click(blocked)
        self.assertNotIn(blocked, self.game.arrows)

    def test_T04_clear_level(self):
        for number, level in enumerate(LEVELS):
            for arrow in solution(level):
                self.click(arrow)
            if number < len(LEVELS) - 1:
                self.assertEqual(self.game.state, "won")
                self.game.advance()
                self.assertEqual(self.game.level, number + 1)
                self.assertEqual(self.game.state, "playing")
            else:
                self.assertEqual(self.game.state, "finished")

    def test_T05_misses_exhausted(self):
        for _ in range(3):
            self.click(LEVELS[0][0])
        self.assertEqual(self.game.state, "lost")
        self.game.advance()
        self.assertEqual(self.game.state, "playing")
        self.assertEqual(self.game.misses, 3)

    def test_T06_restart(self):
        self.click(LEVELS[0][1])
        self.game.reset()
        self.assertEqual(self.game.arrows, list(LEVELS[0]))
        self.assertEqual(self.game.misses, 3)


if __name__ == "__main__":
    unittest.main()
