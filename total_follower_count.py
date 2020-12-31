import csv

import twitch_api
import twitch_cred
from channel import channel_list


def get_online() -> [(str, str, int)]:
    cred = twitch_api.get_cred(twitch_cred.clientID, twitch_cred.secret)
    total_list = list(map(lambda c: (c[0], c[1], twitch_api.get_follower_count(cred, c[0])), channel_list))

    for t in total_list:
        channel_id, channel_name, total = t
        print(f'{channel_name}, {total}')

    with open(f'data/channel_totals.csv', 'w', newline='') as csv_file:
        w = csv.writer(csv_file,
                       delimiter=',',
                       quotechar='|',
                       quoting=csv.QUOTE_MINIMAL)
        w.writerow(['channel_id', 'channel_name', 'total'])
        for t in total_list:
            channel_id, channel_name, total = t
            w.writerow([channel_id, channel_name, total])
    return total_list


def get_local() -> [(str, str, int)]:
    total_list: [(str, str, int)] = []
    with open(f'data/channel_totals.csv', 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        for r in list(reader)[1:]:
            total_list.append((r[0], r[1], int(r[2])))
    return total_list


def _list_sum(sub_list: [(str, str, int)]) -> int:
    return sum(map(lambda x: x[2], sub_list))


def _move(o: [[(str, str, int)]], from_pos: (int, int), to_list: int) -> [[(str, str, int)]]:
    new_list = [[] for _ in range(len(o))]
    list1, pos1 = from_pos
    try:
        if 0 > pos1 >= len(o[list1]):
            return o

        for l in range(len(o)):
            for p in range(len(o[l])):
                element = o[l][p]
                if l != list1 or p != pos1:
                    new_list[l].append(element)

        new_list[to_list].append(o[list1][pos1])
        # print(f'old_score={calc_score(o)}')
        # print(f'new_score={calc_score(new_list)}')
        return new_list
    except IndexError:
        pass
        # print(f'IndexError{from_pos}, {to_list}, {len(new_list)}, {len(o[list1])}')
    return o


def _avg_per_list(o: [[(str, str, int)]]) -> int:
    number_of_sub_lists = len(o)
    sums = list(map(lambda s: _list_sum(s), o))
    total_sum = sum(sums)
    return total_sum // number_of_sub_lists


def _calc_score(o: [[(str, str, int)]]) -> int:
    number_of_sub_lists = len(o)
    sums = list(map(lambda s: _list_sum(s), o))
    total_sum = sum(sums)
    avg = total_sum // number_of_sub_lists
    return sum(map(lambda i: abs(avg - i), sums))


def _optimize(o: [[(str, str, int)]], max_runs=10) -> [[(str, str, int)]]:
    if max_runs == 0:
        return o
    number_of_sub_lists = len(o)
    longest_sub_list = max(map(lambda s: len(s), o))
    current_score = _calc_score(o)
    new_best_o = _move(o, (0, 0), 1)

    for from_list in range(number_of_sub_lists):
        for pos in range(longest_sub_list):
            for to_list in range(number_of_sub_lists):
                temp = _move(o, (from_list, pos), to_list)
                if _calc_score(temp) < _calc_score(new_best_o):
                    new_best_o = temp
    if _calc_score(new_best_o) < current_score:
        return _optimize(new_best_o, max_runs=max_runs - 1)
    print(f'ruturn on run {max_runs}')
    return new_best_o


def _init_list(l: [(str, str, int)], num: int):
    l = list(reversed(sorted(l, key=lambda x: x[2], )))
    r: [[(str, str, int)]] = [[] for _ in range(num)]
    for item in l:
        r[0].append(item)
    return r


def balance(l: [(str, str, int)], num=4) -> [[(str, str, int)]]:
    return _optimize(_init_list(l, num))


def _b(ls: [(str, str, int)], num=4) -> [[(str, str, int)]]:
    if len(ls) >= num:
        return ls
    n_ls = []
    a = _avg_per_list(ls)
    for sub_list in ls:
        s = _list_sum(sub_list)
        if s >= a and len(ls) < num and len(sub_list) > 1:
            s1 = sub_list[:len(sub_list) // 2]
            s2 = sub_list[len(sub_list) // 2:]
            n_ls.append(s1)
            n_ls.append(s2)
        else:
            n_ls.append(sub_list)
    if len(n_ls) == len(ls):
        return ls
    return _b(n_ls, num=num)


def balance2(l: [(str, str, int)], num=4) -> [[(str, str, int)]]:
    ls = _optimize(_init_list(l, num))
    return _b(list(filter(lambda s: len(s) > 0, ls)), num=num)


if __name__ == '__main__':
    for sub_list in balance(get_local(), 16):
        if len(sub_list) > 0:
            print(f'{_list_sum(sub_list)}, {sub_list}')
    print('---')
    for sub_list in balance2(get_local(), 16):
        if len(sub_list) > 0:
            print(f'{_list_sum(sub_list)}, {sub_list}')
