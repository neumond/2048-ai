from math import log
from game import size, flow_line, merge_line, get_val, set_val


KOEF = 0.4
g_backtrack = 3


def emptycells(s):
    return len(list(filter(lambda x: x == 0, s)))


def foldweight(n):
    return log(n, 1.5)


def failcoeff(jumpover, ecells):
    return (jumpover / ecells) if jumpover > 0 else 0


# TODO: duplication of code
def aimove(s, direct):
    backward = direct == 1 or direct == 2
    vert = direct == 0 or direct == 2

    r2args = (size - 1, -1, -1) if backward else (0, size, 1)
    movements = 0
    ecells = emptycells(s)
    folds, foldsum, failpoints = 0, 0, 0
    for c1 in range(size):
        point = size - 1 if backward else 0
        last = None
        jumps = 0
        for c2 in range(*r2args):
            x, y = (c1, c2) if vert else (c2, c1)

            v = get_val(s, x, y)
            if v == 0:
                jumps += 1
                continue

            set_val(s, x, y, 0)

            if v == last:  # fold!
                point -= -1 if backward else 1
                v += last
                folds += 1
                xval = foldweight(v)
                foldsum += xval
                failpoints = xval * failcoeff(jumps, ecells)
                last = None
            else:
                last = v

            jumps = 0

            if vert:
                set_val(s, x, point, v)
            else:
                set_val(s, point, y, v)

            if point != c2:
                movements += 1

            point += -1 if backward else 1
    return movements, folds, foldsum, failpoints


def move_tree(state, backtrack):
    if backtrack <= 0:
        return 0
    maxfldsum = 0
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum, failsum = aimove(s, direct)
        if mvs <= 0:
            continue
        fldsum -= failsum
        fldsum += move_tree(s, backtrack - 1) * KOEF
        maxfldsum = max(maxfldsum, fldsum)
    return maxfldsum


def choose_move(state):
    bestmove, bestmove_dir = None, None
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum, failsum = aimove(s, direct)
        if mvs <= 0:
            continue
        fldsum += move_tree(s, g_backtrack)
        if bestmove is None or fldsum > bestmove:
            bestmove, bestmove_dir = fldsum, direct
    return bestmove_dir
