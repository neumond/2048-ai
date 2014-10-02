import random


size = 4
prob_4 = 1/3  # TODO: not actually proper, original game have 10%


def get_val(s, x, y):
    return s[x + y*size]


def set_val(s, x, y, val):
    s[x + y*size] = val


def flow_line(row):
    for i, v in enumerate(row):
        if v == 0:
            continue
        for cur_idx in range(i - 1, -1, -1):
            cur = row[cur_idx]
            if cur == 0:  # move
                row[cur_idx] = row[cur_idx + 1]
                row[cur_idx + 1] = 0


def merge_line(row):
    for cur_idx in range(len(row) - 1):
        nxt_idx = cur_idx + 1
        cur, nxt = row[cur_idx], row[nxt_idx]
        if cur == nxt:
            row[cur_idx] = cur * 2
            for shift_idx in range(nxt_idx + 1, len(row)):
                row[shift_idx - 1] = row[shift_idx]
            row[-1] = 0


def enum_move_rows(s, direct):
    backward = direct == 1 or direct == 2
    vert = direct == 0 or direct == 2
    r2args = (size - 1, -1, -1) if backward else (0, size, 1)
    for c1 in range(size):
        row = []
        for c2 in range(*r2args):
            x, y = (c1, c2) if vert else (c2, c1)
            row.append(get_val(s, x, y))
        yield row
        for i, c2 in enumerate(range(*r2args)):
            x, y = (c1, c2) if vert else (c2, c1)
            set_val(s, x, y, row[i])


def move(s, direct):
    for row in enum_move_rows(s, direct):
        flow_line(row)
        merge_line(row)


def row_movable(row):
    for i in range(len(row) - 1):
        a, b = row[i:i+2]
        if (a != 0 and a == b) or (a == 0 and b != 0):
            return True
    return False


def can_move(s, direct):
    for row in enum_move_rows(s, direct):
        if row_movable(row):
            return True
    return False


def is_final(s):
    return not any(can_move(s, direct) for direct in range(4))


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
        if random.random() < prob_4:
            s[j] = 4
        else:
            s[j] = 2
        return True
    raise Exception('Random cell not found')


def main():
    from newai import choose_move
    from numprint import print_state

    #from os.path import getmtime
    #vers = getmtime('game.py')

    s = [0] * size * size
    for i in range(3):
        put_random(s)
    print_state(size, s)

    dnames = ['⇈', '⇉', '⇊', '⇇']

    counter = 0
    while not is_final(s):
        direct = choose_move(s)
        if direct is None:
            print('AI can\'t find the move')
            break

        move(s, direct)
        put_random(s)

        counter += 1
        print('{}. Moving {}'.format(counter, dnames[direct]))
        print_state(size, s)

    print('GAME OVER')
    print('Maximum is {}'.format(max(s)))

    #with open('top.txt', 'a') as f:
        #f.write('{}: {}\n'.format(vers, max(s)))


if __name__ == '__main__':
    main()
