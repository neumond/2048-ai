import unittest
from game import *

# dir: 0 - up, 1 - right, 2 - down, 3 - left
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
        b, a = merge_cells({
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
        #self.assertEqual(a, {
            #(4, 2): 2/16,
            #(4, 3): 3/16,
            #0: 11/16,
        #})


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
          {0: .25, (2, 2): .25, (4, 1): .5},
          {(2, 3): 1.},
          {0: 1.},
          {0: 1.},
        ], [
          {0: .25, 4: .75},
          {0: .25, 2: .75},
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
          {0: .125, 4: .375, 8: .5},
          {0: .875, 4: .125},
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


if __name__ == '__main__':
    unittest.main()
