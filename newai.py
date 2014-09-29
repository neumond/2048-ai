from copy import deepcopy
from itertools import product
import random
from game import size, flow_line, merge_line, enum_move_rows, prob_4, move, can_move


epsilon = 0.001
g_backtrack = 1


def _d_add(d, k, val):
    d[k] = d.get(k, 0) + val


def _d_getzero(d):
    return d.get(0, 0.)


def _d_filter_level(d, func):
    return map(lambda x: list(x), filter(lambda x: x[0] != 0 and func(x[0][1]), d.items()))


def flow_prob_line(row):
    row2 = [{(k, i) if k != 0 else 0: v for k, v in v.items()} for i, v in enumerate(row)]
    for i, v in enumerate(row2):
        v = v.copy()
        pass_prob = 1.
        for cur_idx in range(i - 1, -1, -1):
            cur = row2[cur_idx]
            prev = row2[cur_idx + 1]
            prev_whole = sum(map(lambda x: x[1], filter(lambda x: x[0] == 0 or x[0][1] >= i, prev.items())))
            pass_prob *= cur.get(0, 0.) / prev_whole
            if pass_prob == 0.:
                break
            flowsum = 0.
            for number, prob in v.items():
                if number == 0 or prob == 0.:
                    continue
                flow = prob * pass_prob
                if flow != 0.:
                    cur[number] = cur.get(number, 0.) + flow
                    prev[number] = prev.get(number, 0.) - flow
                    flowsum += flow
            if flowsum != 0.:
                cur[0] = cur.get(0, 0.) - flowsum
                prev[0] = prev.get(0, 0.) + flowsum
    row.clear()
    for v in row2:
        row.append(v)


def merge_cells(base, add):
    def filter_items(items):
        return list(filter(lambda x: x[1] > 0., items))

    def convert_zero_back(d):
        if (0, -1) in d:
            d[0] = d.pop((0, -1))
        else:
            d[0] = 0.

    # all keys, except 0, must be tuples
    base_result = {}
    add_result = {}
    base_super_range = sum(map(lambda x: x[1], base.items()))
    add_super_range = sum(map(lambda x: x[1], add.items()))
    assert abs(base_super_range - 1.) < epsilon
    assert abs(add_super_range - 1.) < epsilon

    # remove space
    s = _d_getzero(base)
    add_zero = _d_getzero(add) - s
    if add_zero < -epsilon:
        raise Exception('add_zero < 0 ({}), probably bad input, must be valid Flow result'.format(add_zero))
    _d_add(base_result, (0, -1), s)
    _d_add(add_result, (0, -1), s)

    base_items = []
    add_items = [[(0, -1), add_zero]]
    del add_zero
    shift_levels = {}
    for level in range(size - 1, -1, -1):
        add_items.extend(list(_d_filter_level(add, lambda x: x == level + 1)))
        base_items.extend(list(_d_filter_level(base, lambda x: x == level)))
        add_range = sum(map(lambda x: x[1], add_items))
        if add_range == 0.:
            continue
        item_apply = []
        for add_item, base_item in product(add_items, base_items):
            intersect = (base_item[1]) * (add_item[1] / add_range)  # * (1. / base_super_range)
            if add_item[0][0] == base_item[0][0] and add_item[0][1] > base_item[0][1]:
                # equal numbers, can merge
                _d_add(base_result, add_item[0][0] * 2, intersect)
                item_apply.append((base_item, intersect))
                item_apply.append((add_item, intersect))
                _d_add(shift_levels, add_item[0][1], intersect)
            else:
                # not equal, cannot merge
                _d_add(base_result, base_item[0], intersect)
                _d_add(add_result, add_item[0], intersect)
                item_apply.append((base_item, intersect))
                item_apply.append((add_item, intersect))
        for item, intersect in item_apply:
            item[1] -= intersect
            if item[1] < -epsilon:
                raise Exception('After applying intersect item became negative: - {} = {}'.format(intersect, item[1]))
        add_items = filter_items(add_items)
        base_items = filter_items(base_items)
    convert_zero_back(base_result)
    convert_zero_back(add_result)
    return base_result, add_result, shift_levels


def shift_prob_line(row, toidx, levels):
    sm = sum(levels.values())
    for target_idx in range(toidx, size - 1, 1):
        next_levels = {}
        src = row[target_idx + 1]
        target = row[target_idx]

        for level in range(size - 1, -1, -1):
            levK = levels.get(level, 0.)  # taken amount from pyramid base, we need compensate it
            items = list(_d_filter_level(src, lambda x: x >= level))  # affected pyramid part
            zero_range = 0.
            items_range = sum(map(lambda x: x[1], items))  # size of next level of pyramid
            if items_range < levK:  # level falls completely
                zero_range = levK - items_range
                assert zero_range <= _d_getzero(src) + epsilon
            workedK = 0.
            if items_range + zero_range > 0.:
                for item in items:
                    intersect = item[1] * levK / (items_range + zero_range)
                    key = item[0]
                    _d_add(target, key, intersect)
                    _d_add(src, key, -intersect)  # TODO: apply immediately or defer?
                    _d_add(next_levels, item[0][1], intersect)
                    workedK += intersect
            if workedK < levK:
                intersect = levK - workedK
                assert intersect <= zero_range + epsilon
                _d_add(target, 0, intersect)
                _d_add(src, 0, -intersect)
                _d_add(next_levels, -1, intersect)

        if -1 in levels:
            intersect = levels[-1]
            _d_add(target, 0, intersect)
            _d_add(src, 0, -intersect)  # TODO: apply immediately or defer?
            _d_add(next_levels, -1, intersect)

        levels = next_levels
        assert abs(sm - sum(levels.values())) < epsilon
    _d_add(row[size - 1], 0, sm)


# debug only
# for testing flow&merge
def brute_force_row(row, count=1000):
    flatrow = [list(v.items()) for v in row]  # for stable randoms
    stats = [{} for v in row]
    for i in range(count):
        tryrow = []
        for item in flatrow:
            choo = random.random()
            ch_count = 0.
            choose = None
            for k, v in item:
                ch_count += v
                if ch_count >= choo:
                    choose = k
                    break
            if choose is None:
                choose = item[-1][0]
            tryrow.append(choose)
        flow_line(tryrow)
        merge_line(tryrow)
        for k, item in enumerate(tryrow):
            _d_add(stats[k], item, 1)
    return [{k: v/count for k, v in item.items()} for item in stats]


def merge_prob_line(row):
    for cur_idx in range(len(row) - 1):
        nxt_idx = cur_idx + 1
        cur, nxt = row[cur_idx], row[nxt_idx]

        cur, nxt, shift_levels = merge_cells(cur, nxt)
        row[cur_idx] = cur
        row[nxt_idx] = nxt

        if shift_levels:
            shift_prob_line(row, nxt_idx, shift_levels)

    # flatten dicts
    for cur in row:
        for k, v in cur.copy().items():
            if not isinstance(k, tuple):
                continue
            number = k[0]
            _d_add(cur, number, v)
            del cur[k]


def check_and_clean_row(row):
    for cur in row:
        s = sum(cur.values())
        if abs(s - 1.) > epsilon:
            raise Exception('Invalid prob sum {} for {}'.format(s, cur))
        for k, v in list(cur.items()):
            if not (-epsilon <= v <= (1. + epsilon)):
                raise Exception('Invalid value {} for key {} in {}'.format(v, k, cur))
            if v < 0.:
                v = 0.
            if v > 1.:
                v = 1.
            if v == 0.:
                del cur[k]


def probmove(s, direct):
    for row in enum_move_rows(s, direct):
        check_and_clean_row(row)
        flow_prob_line(row)
        check_and_clean_row(row)
        merge_prob_line(row)
        check_and_clean_row(row)


def put_random_prob(s):
    emptycount = sum(v[0] if 0 in v else 0. for v in s)
    if emptycount == 0:
        return False
    for v in s:
        if 0 not in v:
            continue
        inter2 = (1 - prob_4) * v[0] / emptycount
        inter4 = prob_4 * v[0] / emptycount
        _d_add(v, 2, inter2)
        _d_add(v, 4, inter4)
        _d_add(v, 0, -(inter2 + inter4))
    return True


def make_prob_state(s):
    return [{v: 1.} for v in s]


def move_tree(state, backtrack):
    if backtrack <= 0:
        return sum(_d_getzero(v) for v in state)  # best is most empty
    state = deepcopy(state)
    put_random_prob(state)
    x = []
    for direct in range(4):
        s = deepcopy(state)
        probmove(s, direct)
        x.append(move_tree(s, backtrack - 1))
    return min(x)


def choose_move(state):
    bestmove, bestmove_dir = None, None
    for direct in range(4):
        if not can_move(state, direct):
            continue
        s = state.copy()
        move(s, direct)
        fldsum = move_tree(make_prob_state(s), g_backtrack)
        if bestmove is None or fldsum > bestmove:
            bestmove, bestmove_dir = fldsum, direct
    return bestmove_dir
