import random
from math import log



def color(text, col, bold=True):
    'Wraps a text with terminal color codes'
    bl = ';1' if bold else ''
    return '\x1B[' + col + bl + 'm' + str(text) + '\x1B[39;0m'

color._RED     = '31'
color._GREEN   = '32'
color._YELLOW  = '33'
color._BLUE    = '34'
color._MAGENTA = '35'
color._CYAN    = '36'
color._WHITE   = '37'

color.RED     = '91'
color.GREEN   = '92'
color.YELLOW  = '93'
color.BLUE    = '94'
color.MAGENTA = '95'
color.CYAN    = '96'
color.WHITE   = '97'


nummap = {
  2: (color._WHITE, False),
  4: (color.WHITE, False),
  8: (color._YELLOW, False),
  16: (color.YELLOW, False),
  32: (color._CYAN, False),
  64: (color.CYAN, False),
  128: (color._GREEN, False),
  256: (color.GREEN, False),
  512: (color.GREEN, True),
  1024: (color.RED, True),
  2048: (color.MAGENTA, True),
}




size = 4

def get_val(s, x, y):
    return s[x + y*size]


def set_val(s, x, y, val):
    s[x + y*size] = val


def print_state(s):
    for y in range(size):
        for x in range(size):
            v = get_val(s, x, y)
            print('|{}'.format(color('{:4d}'.format(v), *nummap.get(v, (color._WHITE, False)))) if v else '|    ', end='')
        print('|')
    print()

# dir: 0 - up, 1 - right, 2 - down, 3 - left

def move(s, direct):
    backward = direct == 1 or direct == 2
    vert = direct == 0 or direct == 2

    r2args = (size - 1, -1, -1) if backward else (0, size, 1)
    movements = 0
    folds, foldsum = 0, 0
    for c1 in range(size):
        point = size - 1 if backward else 0
        last = None
        for c2 in range(*r2args):
            x, y = (c1, c2) if vert else (c2, c1)

            v = get_val(s, x, y)
            if v == 0:
                continue

            set_val(s, x, y, 0)

            if v == last:  # fold!
                point -= -1 if backward else 1
                v += last
                folds += 1
                #foldsum += int(log(v, 2))
                foldsum += log(v, 1.5)
                #foldsum += v
                last = None
            else:
                last = v

            if vert:
                set_val(s, x, point, v)
            else:
                set_val(s, point, y, v)

            if point != c2:
                movements += 1

            point += -1 if backward else 1
    return movements, folds, foldsum


def pathcells(s, direct):
    backward = direct == 1 or direct == 2
    vert = direct == 0 or direct == 2
    r2args = (size - 1, -1, -1) if not backward else (0, size, 1)
    pcells = 0
    for c1 in range(size):
        started = False
        for c2 in range(*r2args):
            x, y = (c1, c2) if vert else (c2, c1)
            v = get_val(s, x, y)
            if started:
                if v != 0:
                    continue
                pcells += 1
            else:
                if v != 0:
                    started = True
    return pcells


def emptycells(s):
    return len(list(filter(lambda x: x == 0, s)))


def put_random(s):
    emptycount = len(list(filter(lambda x: x == 0, s)))
    if emptycount == 0:
        return False
    i = random.randrange(0, emptycount)
    for j, v in enumerate(s):
        if v != 0:
            continue
        if i > 0:
            i -= 1
            continue
        s[j] = random.choice([2, 2, 4])
        return True
    raise Exception('Random cell not found')


s = [0] * size * size
for i in range(3):
    put_random(s)
print_state(s)

dnames = ['↑', '→', '↓', '←']


def move_tree(state, backtrack):
    maxfldsum = 0
    ecells = emptycells(state)
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum = move(s, direct)
        pc = pathcells(state, direct)
        if pc > ecells:
            raise Exception('Pathcells > Emptycells: {} > {}'.format(pc, ecells))
        if mvs > 0:
            if backtrack > 0:
                fldsum += move_tree(s, backtrack - 1)
            if pc > 0:
                fldsum *= (1 - pc / ecells)
            maxfldsum = max(maxfldsum, fldsum)
    return maxfldsum


def choose_move(state):
    bestmove, bestmove_dir = None, None
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum = move(s, direct)
        fldsum += move_tree(s, 6)
        if mvs > 0 and (bestmove is None or fldsum > bestmove):
            bestmove, bestmove_dir = fldsum, direct
    #print('bestmove={}'.format(bestmove))
    return bestmove_dir


counter = 0
while True:
    bestmove_dir = choose_move(s)
    rnd = False
    if bestmove_dir is not None:
        mvs, flds, fldsum = move(s, bestmove_dir)
        rnd = put_random(s)
    if bestmove_dir is None or not rnd:
        break
    counter += 1
    print('{}. Moving {}, {} movements'.format(counter, dnames[bestmove_dir], mvs))
    print_state(s)


print('GAME OVER')
print('Maximum is {}'.format(max(s)))

with open('top.txt', 'a') as f:
    f.write('{}\n'.format(max(s)))
