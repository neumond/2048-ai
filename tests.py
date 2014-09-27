import unittest
from game import *

# dir: 0 - up, 1 - right, 2 - down, 3 - left
M_UP = 0
M_RIGHT = 1
M_DOWN = 2
M_LEFT = 3

class MoveNoFoldTest(unittest.TestCase):
    def test_move_empty(self):
        s = [
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
        ]
        r = move(s, M_UP)
        self.assertEqual(s, [
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
        ])
        self.assertEqual(r, (0, 0, 0, 0))

    def test_move_no_fold_up(self):
        s = [
          8, 0, 4, 0,
          0, 2, 2, 8,
          16,0, 0, 0,
          0, 4, 0, 2,
        ]
        r = move(s, M_UP)
        self.assertEqual(s, [
          8, 2, 4, 8,
          16,4, 2, 2,
          0, 0, 0, 0,
          0, 0, 0, 0,
        ])
        self.assertEqual(r, (5, 0, 0, 0))

    def test_move_no_fold_down(self):
        s = [
          8, 0, 4, 0,
          0, 2, 2, 8,
          16,0, 0, 0,
          0, 4, 0, 2,
        ]
        r = move(s, M_DOWN)
        self.assertEqual(s, [
          0, 0, 0, 0,
          0, 0, 0, 0,
          8, 2, 4, 8,
          16,4, 2, 2,
        ])
        self.assertEqual(r, (6, 0, 0, 0))

    def test_move_no_fold_left(self):
        s = [
          8, 0, 4, 0,
          0, 2, 0, 8,
          16,0, 2, 0,
          0, 4, 0, 2,
        ]
        r = move(s, M_LEFT)
        self.assertEqual(s, [
          8, 4, 0, 0,
          2, 8, 0, 0,
          16,2, 0, 0,
          4, 2, 0, 0,
        ])
        self.assertEqual(r, (6, 0, 0, 0))

    def test_move_no_fold_right(self):
        s = [
          8, 0, 4, 0,
          0, 2, 0, 8,
          16,0, 2, 0,
          0, 4, 0, 2,
        ]
        r = move(s, M_RIGHT)
        self.assertEqual(s, [
          0, 0, 8, 4,
          0, 0, 2, 8,
          0, 0, 16,2,
          0, 0, 4, 2,
        ])
        self.assertEqual(r, (6, 0, 0, 0))


class MoveFoldTest(unittest.TestCase):
    def test_fold_up(self):
        s = [
          8, 0, 0, 8,
          0, 0, 2, 8,
          8, 4, 0, 0,
          0, 4, 2, 0,
        ]
        r = move(s, M_UP)
        self.assertEqual(s, [
          16,8, 4, 16,
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
        ])
        self.assertEqual(r[:2], (6, 4))

    def test_fold_down(self):
        s = [
          8, 0, 0, 8,
          0, 0, 2, 8,
          8, 4, 0, 0,
          0, 4, 2, 0,
        ]
        r = move(s, M_DOWN)
        self.assertEqual(s, [
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
          16,8, 4, 16,
        ])
        self.assertEqual(r[:2], (6, 4))

    def test_fold_left(self):
        s = [
          8, 0, 0, 8,
          0, 0, 2, 2,
          4, 4, 0, 0,
          0, 8, 0, 8,
        ]
        r = move(s, M_LEFT)
        self.assertEqual(s, [
          16,0, 0, 0,
          4, 0, 0, 0,
          8, 0, 0, 0,
          16,0, 0, 0,
        ])
        self.assertEqual(r[:2], (6, 4))

    def test_fold_right(self):
        s = [
          8, 0, 0, 8,
          0, 0, 2, 2,
          4, 4, 0, 0,
          0, 8, 0, 8,
        ]
        r = move(s, M_RIGHT)
        self.assertEqual(s, [
          0, 0, 0, 16,
          0, 0, 0, 4,
          0, 0, 0, 8,
          0, 0, 0, 16,
        ])
        self.assertEqual(r[:2], (5, 4))


class FoldPointsTest(unittest.TestCase):
    def test_empty_right(self):
        s = [
          8, 0, 0, 8,
          0, 0, 0, 0,
          0, 0, 0, 0,
          0, 0, 0, 0,
        ]
        r = move(s, M_RIGHT)
        self.assertEqual(r[2], foldweight(16))
        self.assertEqual(r[3], failcoeff(2, 14) * foldweight(16))

    def test_filled_right(self):
        s = [
          4, 8, 0, 8,
          2, 4, 2, 4,
          4, 2, 4, 2,
          2, 4, 2, 4,
        ]
        r = move(s, M_RIGHT)
        self.assertEqual(r[2], foldweight(16))
        self.assertEqual(r[3], failcoeff(1, 1) * foldweight(16))

    def test_adjacent_right(self):
        s = [
          4, 2, 8, 8,
          2, 4, 2, 4,
          4, 2, 4, 2,
          2, 4, 2, 4,
        ]
        r = move(s, M_RIGHT)
        self.assertEqual(r[2], foldweight(16))
        self.assertEqual(r[3], failcoeff(0, 0) * foldweight(16))
        self.assertEqual(r[3], 0)


class ProbFoldingsTest(unittest.TestCase):
    def test_move_empty(self):
        s = [
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_1(self):
        s = [
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 2: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .5, 2: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_2(self):
        s = [
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 2: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .25, 2: .25, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .75, 2: .25},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_3(self):
        s = [
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 2: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .25, 2: .25, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .75, 2: .25},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_4(self):
        s = [
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .25, 4: .5, 8: .25}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_5(self):
        s = [
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .25, 4: .5, 8: .25}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_6(self):
        s = [
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        self.assertEqual(s, [
          {0: .125, 4: .375, 8: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .875, 4: .125},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                   {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                   {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_move_up_7(self):
        s = [
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_UP)
        x = 1/16
        self.assertEqual(s, [
          {0: x, 4: 4*x, 8: 11*x}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 11*x, 4: 4*x, 8: x}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.},                 {0: 1.}, {0: 1.}, {0: 1.},
        ])


if __name__ == '__main__':
    unittest.main()
