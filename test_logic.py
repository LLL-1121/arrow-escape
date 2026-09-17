import unittest

from logic import DIRECTIONS, LEVELS, SIZE, blocker, solution


class RulesTest(unittest.TestCase):
    def test_clear_blocked_and_edge(self):
        self.assertEqual(blocker([(0, 0, "→"), (0, 3, "↑")], (0, 0, "→")), (0, 3, "↑"))
        self.assertIsNone(blocker([(0, 0, "→"), (0, 3, "↑")], (0, 3, "↑")))
        for arrow in ((0, 0, "↑"), (0, 0, "←"), (5, 5, "↓"), (5, 5, "→")):
            self.assertIsNone(blocker([arrow], arrow))

    def test_all_levels_have_safe_order(self):
        for level in LEVELS:
            self.assertEqual({arrow[2] for arrow in level}, set(DIRECTIONS))
            self.assertEqual(len({arrow[:2] for arrow in level}), len(level))
            self.assertTrue(all(0 <= r < SIZE and 0 <= c < SIZE for r, c, _ in level))
            order = solution(level)
            self.assertIsNotNone(order)
            remaining = list(level)
            for arrow in order:
                self.assertIsNone(blocker(remaining, arrow))
                remaining.remove(arrow)
            self.assertFalse(remaining)


if __name__ == "__main__":
    unittest.main()
