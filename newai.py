from copy import deepcopy
from itertools import product
import random
from numprint import color
from game import size, flow_line, merge_line, enum_move_rows, prob_4, move, can_move


epsilon = 0.00001
g_backtrack = 2


def _d_add(d, k, val):
    d[k] = d.get(k, 0) + val


def _d_get(d, k):
    return d.get(k, 0.)


def _d_getzero(d):
    return d.get(0, 0.)


def _d_filter_level(d, func):
    return map(lambda x: list(x), filter(lambda x: isinstance(x[0], tuple) and func(x[0][1]), d.items()))


def _d_merge(a, b):
    r = deepcopy(a)
    for k, v in b.items():
        _d_add(r, k, v)
    return r


def _d_mult(d, t):
    return {k: v * t for k, v in d.items()}


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

    base_result = {}
    add_result = {}

    # TODO: remove this check? it must be done in check_row_func()
    base_super_range = sum(map(lambda x: x[1], base.items()))
    add_super_range = sum(map(lambda x: x[1], add.items()))
    assert abs(base_super_range - 1.) < epsilon
    assert abs(add_super_range - 1.) < epsilon
    del base_super_range
    del add_super_range

    # remove already merged
    for k, v in base.items():
        if isinstance(k, tuple) or k == 0:
            continue
        _d_add(base_result, k, v)

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
    for level in range(size - 1, -2, -1):
        add_items.extend(list(_d_filter_level(add, lambda x: x == level + 1)))
        base_items = list(_d_filter_level(base, lambda x: x == level))
        add_range = sum(map(lambda x: x[1], add_items))
        base_range = sum(map(lambda x: x[1], base_items))
        assert -epsilon < add_range < 1. + epsilon
        assert -epsilon < base_range < 1. + epsilon
        if base_range - add_range > epsilon:
            print('base=', base)
            print('add=', add)
            print('level=', level)
            print('base_range > add_range {} > {}. base {} cannot fit into {}'.format(base_range, add_range, base_items, add_items))
            raise Exception('Invalid pyramid structure')
        if add_range == 0.:
            continue
        item_apply = []
        for add_item, base_item in product(add_items, base_items):
            if not(-epsilon < add_item[1] <= 1. + epsilon):
                raise Exception('Bad add_item: {}'.format(add_item))
            if not(-epsilon < base_item[1] <= 1. + epsilon):
                raise Exception('Bad base_item: {}'.format(base_item))
            intersect = (base_item[1]) * (add_item[1] / add_range)  # * (1. / base_super_range)
            if add_item[0][0] == base_item[0][0] and add_item[0][1] > base_item[0][1]:
                # equal numbers, can merge
                _d_add(base_result, add_item[0][0] * 2, intersect)
                _d_add(shift_levels, add_item[0][1], intersect)
                item_apply.append((add_item, intersect))
                # WARNING: merge removes tuple keys!
            else:
                # not equal, cannot merge
                _d_add(base_result, base_item[0], intersect)
                _d_add(add_result, add_item[0], intersect)
                item_apply.append((add_item, intersect))
        add_items_2 = deepcopy(add_items)
        base_items_2 = deepcopy(base_items)
        for item, intersect in item_apply:
            item[1] -= intersect
            if item[1] < -epsilon:
                print('base=', base)
                print('add=', add)
                print('level=', level)
                print('add_items=', add_items_2)
                print('base_items=', base_items_2)
                print('item_apply=', item_apply)
                raise Exception('After applying intersect item became negative: - {} = {}'.format(intersect, item[1]))
        add_items = filter_items(add_items)
        base_items = filter_items(base_items)
    convert_zero_back(base_result)
    convert_zero_back(add_result)
    return base_result, add_result, shift_levels


def validate_pyramid_cells(base, add):
    vlog = []

    def check(base_range, add_range, level):
        vlog.append('{} <= {} at level {} (rest={})'.format(base_range, add_range, level, add_range - base_range))
        if base_range - add_range > epsilon:
            print(color('{}'.format(base), color.RED))
            print(color('{}'.format(add), color.RED))
            for rec in vlog:
                print('    {}'.format(rec))
            print('base_range > add_range {} > {}. {} cannot fit into {}'.format(base_range, add_range, base, add))
            raise Exception('Invalid pyramid structure detected by validator')

    base_range = _d_getzero(base)
    add_range = _d_getzero(add)
    check(base_range, add_range, -1)
    add_range -= base_range
    for level in range(size - 1, -1, -1):
        add_range += sum(map(lambda x: x[1], _d_filter_level(add, lambda x: x == level + 1)))
        base_range = sum(map(lambda x: x[1], _d_filter_level(base, lambda x: x == level)))
        check(base_range, add_range, level)
        add_range -= base_range


def validate_pyramid_line(row, from_index=0):
    for base, add in zip(row[from_index:], row[from_index + 1:]):
        validate_pyramid_cells(base, add)


def shift_prob_line(row, toidx, levels):
    sm = sum(levels.values())
    for target_idx in range(toidx, size - 1, 1):
        next_levels = {}
        src = row[target_idx + 1]
        target = row[target_idx]

        if -1 in levels:
            intersect = levels[-1]
            _d_add(target, 0, intersect)
            _d_add(src, 0, -intersect)  # TODO: apply immediately or defer?
            _d_add(next_levels, -1, intersect)

        for level in range(size - 1, -1, -1):
            levK = levels.get(level, 0.)  # taken amount from pyramid base, we need compensate it
            if levK <= 0.:
                continue
            items = list(_d_filter_level(src, lambda x: x > level))  # affected pyramid part
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
                    if not isinstance(key, tuple) and key != 0:
                        raise Exception('Shift: wrong key {}'.format(key))
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
    validate_pyramid_line(row)
    for cur_idx in range(len(row) - 1):
        nxt_idx = cur_idx + 1
        cur, nxt = row[cur_idx], row[nxt_idx]
        validate_pyramid_line(row, cur_idx)

        cur, nxt, shift_levels = merge_cells(cur, nxt)

        row[cur_idx] = cur
        row[nxt_idx] = nxt

        if shift_levels:
            if -1 in shift_levels:
                _d_add(shift_levels, None, shift_levels[-1])
                del shift_levels[-1]
            shift_prob_line2(row, nxt_idx, shift_levels)

        check_and_clean_row(row, clean=False)

    # flatten dicts
    for cur in row:
        for k, v in cur.copy().items():
            if not isinstance(k, tuple):
                continue
            number = k[0]
            _d_add(cur, number, v)
            del cur[k]


def check_and_clean_row(row, clean=True):
    for cur in row:
        s = sum(cur.values())
        if abs(s - 1.) > epsilon:
            raise Exception('Invalid prob sum {} for {}'.format(s, cur))
        for k, v in list(cur.items()):
            if not (-epsilon <= v <= (1. + epsilon)):
                raise Exception('Invalid value {} for key {} in {}'.format(v, k, cur))
            if not clean:
                continue
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
        validate_pyramid_line(row)
        check_and_clean_row(row)
        validate_pyramid_line(row)
        merge_prob_line(row)
        check_and_clean_row(row)


class InvalidPyramidException(Exception):
    pass
class InvalidShiftLevelAmountException(Exception):
    pass


def required_levels(base, add, merged=False):
    'Returns the part of the add required by the base'

    # cut zero level
    base0 = _d_getzero(base)
    rest_zero = _d_getzero(add)
    if rest_zero < base0:
        raise InvalidPyramidException
    result = {None: {0: base0}}
    rest_zero -= base0
    del base0

    def merge_to_dict(items):
        d = {}
        for k, v in items:
            _d_add(d, k, v)
        return d

    # cut levels
    rest = []
    for level in range(size - 1, -1, -1):
        rest.extend(list(_d_filter_level(add, lambda x: x == level + 1)))
        rest_range = sum(map(lambda x: x[1], rest))
        base_items = list(_d_filter_level(base, lambda x: x == level))
        base_range = sum(map(lambda x: x[1], base_items))
        if base_range > rest_range + rest_zero:
            raise InvalidPyramidException
        # first, annihilate items
        if rest_range > 0.:
            amount = min(rest_range, base_range)
            k = amount / rest_range  # part of item to annihilate
            result[level] = merge_to_dict(map(lambda x: (x[0], x[1] * k), rest))
            k = 1. - k
            rest = list(map(lambda x: (x[0], x[1] * k), rest))
        else:
            result[level] = {}
        # second, fill the rest of the gap with zero level
        amount = max(0., base_range - rest_range)
        _d_add(result[level], 0, amount)
        rest_zero -= amount

    if merged:
        result2 = {}
        for level, d in result.items():
            for k, v in d.items():
                _d_add(result2, k, v)
        return result2

    return result

# TODO: rewrite merge_cells

def shift_empty_space(base, add, levels):
    move = {}

    # cut required zero level
    base0 = _d_getzero(base)
    rest_zero = _d_getzero(add)
    if rest_zero < base0 - epsilon:
        raise InvalidPyramidException
    rest_zero -= base0
    del base0

    # move zero level
    amount = _d_get(levels, None)
    if amount > rest_zero + epsilon:
        raise InvalidShiftLevelAmountException
    _d_add(move, 0, amount)
    rest_zero -= amount

    # require and move levels
    # cut levels
    rest = {}
    for level in range(size - 1, -1, -1):

        #### prepare

        rest = _d_merge(rest, dict(_d_filter_level(add, lambda x: x == level + 1)))
        rest_range = sum(map(lambda x: x[1], rest.items()))
        base_items = dict(_d_filter_level(base, lambda x: x == level))
        base_range = sum(map(lambda x: x[1], base_items.items()))
        lev_amount = _d_get(levels, level)

        #### require by existent base cells

        if base_range > rest_range + rest_zero + epsilon:
            print(base_range, '>', rest_range, '+', rest_zero)
            raise InvalidPyramidException
        # first, annihilate items
        if rest_range > 0.:
            amount = min(rest_range, base_range)
            k = amount / rest_range  # part of item to annihilate
            rest = _d_mult(rest, 1. - k)  # cut required part
        # second, fill the rest of the gap with zero level
        amount = max(0., base_range - rest_range)
        if amount > rest_zero + epsilon:
            print(amount, '>', rest_zero)
            raise InvalidPyramidException
        rest_zero -= amount  # cut required part
        rest_range = sum(map(lambda x: x[1], rest.items()))  # update current state

        #### move items down

        # first, move items
        if rest_range > 0.:
            amount = min(lev_amount, rest_range)
            k = amount / rest_range  # part of item to move down
            move = _d_merge(move, _d_mult(rest, k))
            rest = _d_mult(rest, 1. - k)  # cut moved part
        # second, fill the rest of the gap with zero level
        amount = max(0., lev_amount - rest_range)
        if amount > rest_zero + epsilon:
            print(amount, '>', rest_zero)
            raise InvalidShiftLevelAmountException
        _d_add(move, 0, amount)
        rest_zero -= amount  # cut moved part

    # apply moves
    next_levels = {}
    for k, v in move.items():
        _d_add(base, k, v)
        _d_add(add, k, -v)
        _d_add(next_levels, None if k == 0 else k[1], v)

    return next_levels


def shift_prob_line2(row, toidx, levels):
    sm = sum(levels.values())
    for target_idx in range(toidx, size - 1, 1):
        next_levels = {}
        src = row[target_idx + 1]
        target = row[target_idx]

        next_levels = shift_empty_space(target, src, levels)
        if abs(sm - sum(next_levels.values())) > epsilon:
            raise Exception('Bad level values: was {} become {}'.format(levels, next_levels))
        levels = next_levels
    _d_add(row[size - 1], 0, sm)


def put_random_prob(s):
    emptycount = sum((v[0] if 0 in v else 0.) for v in s)
    #print('emptycount', emptycount)
    if emptycount == 0:
        return False
    for v in s:
        if 0 not in v:
            continue
        inter2 = (1 - prob_4) * v[0] * (v[0] / emptycount)
        inter4 = prob_4 * v[0] * (v[0] / emptycount)
        _d_add(v, 2, inter2)
        _d_add(v, 4, inter4)
        _d_add(v, 0, -(inter2 + inter4))
    return True


def make_prob_state(s):
    return [{v: 1.} for v in s]


def move_tree(state, backtrack):
    if backtrack <= 0:
        return sum(_d_getzero(v) for v in state)  # best is most empty
    old_state = state
    state = deepcopy(state)
    put_random_prob(state)
    for d in state:
        bads = list(filter(lambda x: not(-epsilon < x < 1. + epsilon), d.values()))
        if bads:
            print(old_state)
            print(state)
            raise Exception('Bad put random')
    x = []
    for direct in range(4):
        s = deepcopy(state)
        probmove(s, direct)
        x.append(move_tree(s, backtrack - 1))
    return max(x)


# empty cell count
# merging big numbers
# probability of death


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
