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


def print_num(n, fmt='{}'):
    return color((fmt).format(n), *nummap.get(n, (color._WHITE, False)))


def _get_val(size, s, x, y):
    return s[x + y*size]


def print_state(size, s):
    for y in range(size):
        for x in range(size):
            v = _get_val(size, s, x, y)
            print('|{}'.format(print_num(v, '{:4d}')) if v else '|    ', end='')
        print('|')
    print()
