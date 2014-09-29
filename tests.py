import unittest
from game import *
from newai import probmove, flow_prob_line, merge_prob_line, check_and_clean_row, merge_cells


M_UP = 0
M_RIGHT = 1
M_DOWN = 2
M_LEFT = 3


class FlowLineTest(unittest.TestCase):
    def check(self, a, b):
        flow_line(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([0, 0, 0, 0], [0, 0, 0, 0])
        self.check([0, 0, 2, 0], [2, 0, 0, 0])
        self.check([2, 0, 2, 0], [2, 2, 0, 0])
        self.check([0, 4, 0, 2], [4, 2, 0, 0])
        self.check([2, 2, 2, 2], [2, 2, 2, 2])
        self.check([2, 4, 8,16], [2, 4, 8,16])


class MergeLineTest(unittest.TestCase):
    def check(self, a, b):
        merge_line(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([2, 2, 0, 0], [4, 0, 0, 0])
        self.check([2, 2, 2, 2], [4, 4, 0, 0])
        self.check([2, 4, 4, 8], [2, 8, 8, 0])
        self.check([0, 0, 0, 0], [0, 0, 0, 0])


class LineTest(unittest.TestCase):
    def check(self, a, b):
        flow_line(a)
        merge_line(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([8, 0,16, 0], [8,16, 0, 0])
        self.check([0, 2, 0, 4], [2, 4, 0, 0])
        self.check([8, 0, 8, 0], [16,0, 0, 0])
        self.check([8, 4, 4, 4], [8, 8, 4, 0])


class CanMoveTest(unittest.TestCase):
    def test_row_movable(self):
        self.assertEqual(row_movable([2, 4, 2, 4]), False)
        self.assertEqual(row_movable([0, 4, 2, 4]), True)
        self.assertEqual(row_movable([2, 4, 2, 0]), False)
        self.assertEqual(row_movable([0, 0, 0, 0]), False)
        self.assertEqual(row_movable([8, 0, 0, 0]), False)
        self.assertEqual(row_movable([0, 8, 0, 0]), True)
        self.assertEqual(row_movable([8, 8, 8, 8]), True)


class FlowProbLineTest(unittest.TestCase):
    maxDiff = None
    def check(self, a, b):
        flow_prob_line(a)
        check_and_clean_row(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([
          {0: 1.},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ], [
          {0: 1.},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_2(self):
        self.check([
          {0: 1.},
          {0: 1.},
          {0: .5, 2: .5},
          {0: 1.},
        ], [
          {0: .5, (2, 2): .5},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_3(self):
        self.check([
          {0: 1.},
          {0: .5, 4: .5},
          {0: .5, 2: .5},
          {0: 1.},
        ], [
          {0: .25, (2, 2): .25, (4, 1): .5},
          {0: .75, (2, 2): .25},
          {0: 1.},
          {0: 1.},
        ])

    def test_5(self):
        self.check([
          {0: .5, 4: .5},
          {0: 1.},
          {0: 1.},
          {0: .5, 4: .5},
        ], [
          {0: .25, (4, 0): .5, (4, 3): .25},
          {0: .75, (4, 3): .25},
          {0: 1.},
          {0: 1.},
        ])

    def test_7(self):
        self.check([
          {0: 1.},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
        ], [
          {0: .125, (4, 1): .5, (4, 2): .25, (4, 3): .125},
          {0: .5, (4, 2): .25, (4, 3): .25},
          {0: .875, (4, 3): .125},
          {0: 1.},
        ])

    def test_8(self):
        x = 1/16
        self.check([
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
        ], [
          {0: 1*x, (4, 0): 8*x, (4, 1): 4*x, (4, 2): 2*x, (4, 3): x},
          {0: 5*x, (4, 1): 4*x, (4, 2): 4*x, (4, 3): 3*x},
          {0: 11*x, (4, 2): 2*x, (4, 3): 3*x},
          {0: 15*x, (4, 3): x},
        ])


class MergeCellTest(unittest.TestCase):
    maxDiff = None

    def test_1(self):
        b, a, sh = merge_cells({
            (4, 0): 8/16,
            (4, 1): 4/16,
            (4, 2): 2/16,
            (4, 3): 1/16,
            0: 1/16,
        }, {
            (4, 1): 4/16,
            (4, 2): 4/16,
            (4, 3): 3/16,
            0: 5/16,
        })
        self.assertEqual(b, {
            8: 11/16,
            (4, 0): 1/16,
            (4, 1): 1/16,
            (4, 2): 1/16,
            (4, 3): 1/16,
            0: 1/16,
        })
        #self.assertEqual(sh, {})
        #self.assertEqual(a, {
            #(4, 2): 2/16,
            #(4, 3): 3/16,
            #0: 11/16,
        #})

    def test_2(self):
        b, a, sh = merge_cells({
            (4, 1): 8/16,
            0: 8/16,
        }, {
            (4, 2): 2/16,
            (8, 2): 2/16,
            0: 12/16,
        })
        self.assertEqual(b, {0: 0.5, 8: 0.125, (4, 1): 0.375})
        self.assertEqual(a, {
            (8, 2): 2/16,
            0: 12/16,
        })
        self.assertEqual(sh, {2: 2/16})

    def test_2_1(self):
        b, a, sh = merge_cells({
          0: 2/16,
          (2, 2): 4/16,
          (2, 3): 2/16,
          (4, 1): 8/16,
        }, {
          0: 10/16,
          (2, 3): 6/16,
        })
        self.assertEqual(b, {0: 2/16, (2, 2): 2/16, (2, 3): 2/16, (4, 1): 8/16, 4: 2/16})
        self.assertEqual(a, {0: 10/16, (2, 3): 4/16})
        self.assertEqual(sh, {3: 2/16})


class MergeProbLineTest(unittest.TestCase):
    maxDiff = None
    def check(self, a, b):
        merge_prob_line(a)
        check_and_clean_row(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([
          {0: .25, (2, 2): .25, (4, 1): .5},
          {0: .75, (2, 2): .25},
          {0: 1.},
          {0: 1.},
        ], [
          {0: .25, 2: .25, 4: .5},
          {0: .75, 2: .25},
          {0: 1.},
          {0: 1.},
        ])

    def test_2(self):
        self.check([
          {0: 2/16, (2, 2): 4/16, (2, 3): 2/16, (4, 1): 8/16},
          {0: 10/16, (2, 3): 6/16},
          {0: 1.},
          {0: 1.},
        ], [
          {0: 2/16, 2: 4/16, 4: 10/16},
          {0: 12/16, 2: 4/16},
          {0: 1.},
          {0: 1.},
        ])

    def test_5(self):
        self.check([
          {0: .25, (4, 0): .5, (4, 3): .25},
          {0: .75, (4, 3): .25},
          {0: 1.},
          {0: 1.},
        ], [
          {0: .25, 4: .5, 8: .25},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_7(self):
        self.check([
          {0: .125, (4, 1): .5, (4, 2): .25, (4, 3): .125},
          {0: .5, (4, 2): .25, (4, 3): .25},
          {0: .875, (4, 3): .125},
          {0: 1.},
        ], [
          {0: 1/8, 4: 3/8, 8: 4/8},
          {0: 7/8, 4: 1/8},
          {0: 1.},
          {0: 1.},
        ])

    def test_8(self):
        x = 1/16
        self.check([
          {0: 1*x, (4, 0): 8*x, (4, 1): 4*x, (4, 2): 2*x, (4, 3): x},
          {0: 5*x, (4, 1): 4*x, (4, 2): 4*x, (4, 3): 3*x},
          {0: 11*x, (4, 2): 2*x, (4, 3): 3*x},
          {0: 15*x, (4, 3): x},
        ], [
          {0: x, 4: 4*x, 8: 11*x},
          {0: 11*x, 4: 4*x, 8: x},
          {0: 1.},
          {0: 1.},
        ])


class ProbLineTest(unittest.TestCase):
    maxDiff = None
    def check(self, a, b):
        flow_prob_line(a)
        merge_prob_line(a)
        check_and_clean_row(a)
        self.assertEqual(a, b)

    def test_1(self):
        self.check([
          {0: 1.},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ], [
          {0: 1.},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_2(self):
        self.check([
          {0: 1.},
          {0: 1.},
          {0: .5, 2: .5},
          {0: 1.},
        ], [
          {0: .5, 2: .5},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_3(self):
        self.check([
          {0: 1.},
          {0: .5, 4: .5},
          {0: .5, 2: .5},
          {0: 1.},
        ], [
          {0: .25, 2: .25, 4: .5},
          {0: .75, 2: .25},
          {0: 1.},
          {0: 1.},
        ])

    def test_4(self):
        self.check([
          {0: .5, 4: .5},
          {0: 1.},
          {0: 1.},
          {0: .5, 2: .5},
        ], [
          {0: .25, 2: .25, 4: .5},
          {0: .75, 2: .25},
          {0: 1.},
          {0: 1.},
        ])

    def test_5(self):
        self.check([
          {0: .5, 4: .5},
          {0: 1.},
          {0: 1.},
          {0: .5, 4: .5},
        ], [
          {0: .25, 4: .5, 8: .25},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_6(self):
        self.check([
          {0: 1.},
          {0: .5, 4: .5},
          {0: 1.},
          {0: .5, 4: .5},
        ], [
          {0: .25, 4: .5, 8: .25},
          {0: 1.},
          {0: 1.},
          {0: 1.},
        ])

    def test_7(self):
        self.check([
          {0: 1.},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
        ], [
          {0: .125, 4: .375, 8: .5},
          {0: .875, 4: .125},
          {0: 1.},
          {0: 1.},
        ])

    def test_8(self):
        x = 1/16
        self.check([
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
          {0: .5, 4: .5},
        ], [
          {0: x, 4: 4*x, 8: 11*x},
          {0: 11*x, 4: 4*x, 8: x},
          {0: 1.},
          {0: 1.},
        ])


class ProbMoveTest(unittest.TestCase):
    maxDiff = None

    def test_up(self):
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
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_down(self):
        s = [
          {0: 1.},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .5, 4: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_DOWN)
        self.assertEqual(s, [
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: .875, 4: .125},        {0: 1.}, {0: 1.}, {0: 1.},
          {0: .125, 4: .375, 8: .5}, {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_left(self):
        s = [
          {0: 1.}, {0: .5, 4: .5}, {0: .5, 4: .5}, {0: .5, 4: .5},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_LEFT)
        self.assertEqual(s, [
          {0: .125, 4: .375, 8: .5}, {0: .875, 4: .125}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ])

    def test_right(self):
        s = [
          {0: 1.}, {0: .5, 4: .5}, {0: .5, 4: .5}, {0: .5, 4: .5},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ]
        probmove(s, M_RIGHT)
        self.assertEqual(s, [
          {0: 1.}, {0: 1.}, {0: .875, 4: .125}, {0: .125, 4: .375, 8: .5},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
          {0: 1.}, {0: 1.}, {0: 1.}, {0: 1.},
        ])


if __name__ == '__main__':
    unittest.main()
