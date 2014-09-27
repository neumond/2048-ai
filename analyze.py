from numprint import print_num

aliases = {
  '1411777083.815053':  'no backtracking',
  '1411777371.6336334': '     bt=1 k=1.0',
  '1411777572.9672217': '     bt=2 k=1.0',
  '1411778544.7757337': '     bt=2 k=0.8',
  '1411779085.5464628': '     bt=2 k=0.6',
  '1411779559.8907495': '     bt=2 k=0.4',
  '1411779992.2557008': '     bt=2 k=0.2',
  '1411780389.0331292': '     bt=2 k=0.1',
  '1411780825.3845873': '     bt=3 k=0.4',
}


def main():
    v = {}
    with open('top.txt') as f:
        for line in f:
            ver, pts = line.split(': ')
            if ver not in v:
                v[ver] = {}
            d = v[ver]
            pts = int(pts.strip())
            if pts not in d:
                d[pts] = 0
            d[pts] += 1

    for ver, vals in sorted(v.items(), key=lambda x: x[0]):
        if ver in aliases:
            ver = aliases[ver]
        count = sum(list(vals.values()))
        lst = ' '.join(['{}={:d}%'.format(print_num(k), round(vals[k]/count*100)) for k in sorted(list(vals.keys()))])
        print('{}: {} (count {}, 2k {})'.format(ver, lst, count, vals.get(2048, '-')))


if __name__ == '__main__':
    main()
