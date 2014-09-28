import random
from math import log
from os.path import getmtime
from numprint import print_state


size = 4
KOEF = 0.4


def get_val(s, x, y):
    return s[x + y*size]


def set_val(s, x, y, val):
    s[x + y*size] = val


def foldweight(n):
    return log(n, 1.5)


def failcoeff(jumpover, ecells):
    return (jumpover / ecells) if jumpover > 0 else 0


# dir: 0 - up, 1 - right, 2 - down, 3 - left

def move(s, direct):
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


def flow_line(row):
    for i, v in enumerate(row):
        if v == 0:
            continue
        for cur_idx in range(i - 1, -1, -1):
            cur = row[cur_idx]
            if cur == 0: # move
                row[cur_idx] = row[cur_idx + 1]
                row[cur_idx + 1] = 0


def flow_prob_line(row):
    row2 = [{(k, i) if k != 0 else 0: v for k, v in v.items()} for i, v in enumerate(row)]
    for i, v in enumerate(row2):
        v = v.copy()
        #print('base: #{} {}'.format(i, v))
        pass_prob = 1.
        for cur_idx in range(i - 1, -1, -1):
            cur = row2[cur_idx]
            prev = row2[cur_idx + 1]
            prev_whole = sum(map(lambda x: x[1], filter(lambda x: x[0] == 0 or x[0][1] >= i, prev.items())))
            #print('prev_whole={}'.format(prev_whole))
            pass_prob *= cur.get(0, 0.) / prev_whole
            #print('sub (pass={}): #{} {}'.format(pass_prob, cur_idx, cur))
            if pass_prob == 0.:
                break
            flowsum = 0.
            for number, prob in v.items():
                if number == 0 or prob == 0.:
                    continue
                flow = prob * pass_prob
                #print('  numflow (n={}, flow={})'.format(number, flow))
                if flow != 0.:
                    cur[number] = cur.get(number, 0.) + flow
                    prev[number] = prev.get(number, 0.) - flow
                    flowsum += flow
            if flowsum != 0.:
                cur[0] = cur.get(0, 0.) - flowsum
                prev[0] = prev.get(0, 0.) + flowsum
            #print('  current state {}'.format(row2))
        #print('current state {}'.format(row2))
    row.clear()
    for v in row2:
        row.append(v)


def merge_line(row):
    for cur_idx in range(len(row) - 1):
        nxt_idx = cur_idx + 1
        cur, nxt = row[cur_idx], row[nxt_idx]
        if cur == nxt:
            row[cur_idx] = cur * 2
            for shift_idx in range(nxt_idx + 1, len(row)):
                row[shift_idx - 1] = row[shift_idx]
            row[-1] = 0


def _dict_sum(d):
    return sum(list(map(lambda x: x[1], filter(lambda x: x[0] != 0, d.items()))))


def _mult_dict(d, koef):
    zero = d.get(0, 0.)
    sm = _dict_sum(d)
    zero += sm - sm * koef
    r = {k: v * koef if k != 0 else zero for k, v in d.items()}
    if 0 not in r:
        r[0] = zero
    return r


def _add_dict(a, b):
    r = a.copy()
    sm = _dict_sum(b)
    zero = a.get(0, 0.) - sm
    if zero < 0.:
        raise Exception('Adding dict with overflow: {} + {}'.format(a, b))
    for k, v in b.items():
        r[k] = r.get(k, 0.) + v
    r[0] = zero
    return r


def merge_prob_line(row):
    for cur_idx in range(len(row) - 1):
        nxt_idx = cur_idx + 1
        cur, nxt = row[cur_idx], row[nxt_idx]
        print('Base #{} {}'.format(cur_idx, cur))
        print('         {}'.format(nxt))
        total_shift_prob = 0.
        total_sum = _dict_sum(nxt)
        for number, cur_prob in sorted(cur.copy().items(), key=lambda x: -1 if x[0] == 0 else x[0][1]):
            if number == 0 or cur_prob == 0.:
                continue
            print('  checking {}'.format(number))
            n2 = number[0] * 2
            affected_nxt_items = list(filter(lambda x: x[0][0] == number[0] and x[0][1] > number[1], filter(lambda x: x[0] != 0, nxt.items())))
            print('  affected={}'.format(affected_nxt_items))
            nxt_prob = sum(map(lambda x: x[1], affected_nxt_items))
            #print('nxt_prob={}'.format(nxt_prob))
            if nxt_prob == 0.:
                continue
            merge_prob = min(cur_prob, nxt_prob)
            print('  num={}, merge={}'.format(number[0], merge_prob))
            total_shift_prob += merge_prob
            cur[number] = cur_prob - merge_prob
            cur[n2] = cur.get(n2, 0.) + merge_prob
            for k, v in affected_nxt_items:
                #nxt[k] *= 1 - cur_prob
                nxt[k] = nxt[k] - merge_prob * (nxt[k] / nxt_prob)
            #nxt[number] = nxt_prob - merge_prob
            nxt[0] = nxt.get(0, 0.) + merge_prob
        if total_shift_prob != 0.:
            print('Shift at #{} with k={}'.format(nxt_idx, total_shift_prob))
            print('  before shift {}'.format(row))
            for shift_idx in range(nxt_idx + 1, len(row)):
                # a = b * prob
                # b = b * (1 - prob)
                a, b = row[shift_idx - 1], row[shift_idx]
                #assert sum(list(a.values())) == 1.
                #assert sum(list(b.values())) == 1.
                k = total_shift_prob / total_sum
                a = _add_dict(a, _mult_dict(b, k))
                b = _mult_dict(b, 1 - k)
                row[shift_idx - 1] = a
                row[shift_idx] = b
            #row[-1][0] = row[-1].get(0, 0.) + total_shift_prob
            print('  after shift {}'.format(row))
    # flatten dicts
    for cur in row:
        for k, v in cur.copy().items():
            if not isinstance(k, tuple):
                continue
            number = k[0]
            cur[number] = cur.get(number, 0.) + v
            del cur[k]


def check_and_clean_row(row):
    for cur in row:
        s = sum(cur.values())
        if abs(s - 1.) > 0.001:
            raise Exception('Invalid prob sum {} for {}'.format(s, cur))
        for k, v in list(cur.items()):
            if not (0. <= v <= 1.):
                raise Exception('Invalid value {} for key {} in {}'.format(v, k, cur))
            if v == 0.:
                del cur[k]


# dir: 0 - up, 1 - right, 2 - down, 3 - left

#def probmove(s, direct):
    #backward = direct == 1 or direct == 2
    #vert = direct == 0 or direct == 2

    #r2step = -1 if backward else 1
    #r2args = (size - 1, -1, -1) if backward else (0, size, 1)
    #r2args_1 = (size - 1, 0, -1) if backward else (0, size - 1, 1)
    #def r2args_sub(coord):
        #return (coord + 1, size, 1) if backward else (coord - 1, -1, -1)

    ## store here merged probabilities to exclude cumulative effects
    ## i.e. merge can be done once per move
    #pending_merges = []

    ## merge step
    #for c1 in range(size):
        #for c2 in range(*r2args_1):
            #x, y = (c1, c2) if vert else (c2, c1)
            #xc, yc = (c1, c2 + r2step) if vert else (c2 + r2step, c1)
            #v = get_val(s, x, y)
            #vnext = get_val(s, xc, yc)
            #total_shift_prob = 0.
            #for number, prob in v.items():
                #if number == 0 or number not in vnext:
                    #continue
                #merge_prob = prob * vnext[number]
                #if merge_prob == 0.:
                    #continue
                #total_shift_prob += merge_prob
                ## TODO: merge

            #if total_shift_prob != 0.:
                #for c22 in range(*r2args_sub_1(c2)):

                #prev = v
                ##print('enum for ({}, {}), #{}: '.format(x, y, number), end='')
                #for c22 in range(*r2args_sub(c2)):
                    #xc, yc = (c1, c22) if vert else (c22, c1)
                    ##print('({}, {}) '.format(xc, yc), end='')
                    #vv = get_val(s, xc, yc)

                    #flow = amount * vv.get(0, 0.)
                    #if flow != 0.:
                        #vv[number] = vv.get(number, 0.) + flow
                        #vv[0] = vv.get(0, 0.) - flow
                        #prev[number] = prev.get(number, 0.) - flow
                        #prev[0] = prev.get(0, 0.) + flow

                    #amount = flow
                    #prev = vv
                ##print()

    #for x, y, number, prob in pending_merges:
        #v = get_val(s, x, y)
        #v[number] = v.get(number, 0.) + prob

    #for v in s:
        #if abs(sum(list(v.values())) - 1.0) > 0.001:
            #raise Exception('Sum of probabilities is not 1 ({}): {}'.format(sum(list(v.values())), v))
        #for k in list(v.keys()):
            #if v[k] <= 0.:
                #del v[k]


def probtest(row):
    for c2 in range(size):
        v = row[c2]
        if v == 0:
            continue
        for c22 in range(c2 - 1, -1, -1):
            prev = row[c22 + 1]
            vv = row[c22]

            if isinstance(vv, int) and vv == prev:
                # merge
                row[c22] = (vv * 2,)
                row[c22 + 1] = 0
            elif vv == 0:
                # move
                row[c22] = prev
                row[c22 + 1] = 0
    for c2 in range(size):
        if type(row[c2]) == tuple:
            row[c2] = row[c2][0]


def probtest2(row):
    for c2 in range(size):
        v = row[c2]
        if v == 0:
            continue
        for c22 in range(c2 - 1, -1, -1):
            prev = row[c22 + 1]
            vv = row[c22]
            if vv == 0:
                # move
                row[c22] = prev
                row[c22 + 1] = 0
    for c2 in range(size - 1):
        v = row[c2]
        v1 = row[c2 + 1]
        if v == v1:
            row[c2] = v * 2
            row.pop(c2 + 1)
            row.append(0)
    for c2 in range(size):
        if type(row[c2]) == tuple:
            row[c2] = row[c2][0]


def probstress():
    import random
    p = {}
    for i in range(100000):
        row = []
        for k in range(size):
            row.append(4 if random.random() < 0.5 else 0)
        a, b = row.copy(), row.copy()
        probtest(a)
        probtest2(b)
        assert a == b
        row = tuple(a)
        p[row] = p.get(row, 0) + 1
    #p = {k: v / s for k, v in p.items()}
    res = [{}, {}, {}, {}]
    for k, v in p.items():
        for i in range(size):
            res[i][k[i]] = res[i].get(k[i], 0) + v
    for i in range(size):
        s = sum(res[i].values())
        res[i] = {k: v / s for k, v in res[i].items()}
    return res


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


def move_tree(state, backtrack):
    if backtrack <= 0:
        return 0
    maxfldsum = 0
    ecells = emptycells(state)
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum, failsum = move(s, direct)
        if mvs <= 0:
            continue
        fldsum -= failsum
        fldsum += move_tree(s, backtrack - 1) * KOEF
        maxfldsum = max(maxfldsum, fldsum)
    return maxfldsum


def choose_move(state, backtrack):
    bestmove, bestmove_dir = None, None
    for direct in range(4):
        s = state.copy()
        mvs, flds, fldsum, failsum = move(s, direct)
        fldsum += move_tree(s, backtrack)
        if mvs > 0 and (bestmove is None or fldsum > bestmove):
            bestmove, bestmove_dir = fldsum, direct
    #print('bestmove={}'.format(bestmove))
    return bestmove_dir


def main():
    vers = getmtime('game.py')

    s = [0] * size * size
    for i in range(3):
        put_random(s)
    print_state(size, s)

    dnames = ['↑', '→', '↓', '←']

    counter = 0
    while True:
        backtrack = 0
        if max(s) >= 512:
            backtrack += 1
        if max(s) >= 1024:
            backtrack += 1
        backtrack = 3
        bestmove_dir = choose_move(s, backtrack)
        rnd = False
        if bestmove_dir is not None:
            mvs, flds, fldsum, failsum = move(s, bestmove_dir)
            rnd = put_random(s)
        if bestmove_dir is None or not rnd:
            break
        counter += 1
        print('{}. Moving {}, {} movements'.format(counter, dnames[bestmove_dir], mvs))
        print_state(size, s)


    print('GAME OVER')
    print('Maximum is {}'.format(max(s)))

    with open('top.txt', 'a') as f:
        f.write('{}: {}\n'.format(vers, max(s)))


if __name__ == '__main__':
    main()
