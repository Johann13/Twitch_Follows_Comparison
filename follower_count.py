from typing import overload

from channel import channel_list
from twitch_api import get_cred, get_follower_count, TwitchCredentials
from twitch_cred import clientID, secret

__test_list = [
    ('63839894', 'Checkpoint', 641),
    ('64758947', 'Breeh', 2489),
    ('145983935', 'Bekkiboom', 4252),
    ('79911474', 'brionykay', 4425),
    ('40639871', 'JoeHickson', 4697),
    ('239617169', 'rossperu', 6006),
    ('465613748', 'm4ngo', 6430),
    ('44135610', 'FionaRiches', 6479),
    ('62904151', 'MiniMuka', 6839),
    ('15597175', 'alsmiffy', 6920),
    ('21285936', 'Daltos', 7683),
    ('96502692', 'WilsonatorYT', 8707),
    ('43903922', 'Vadact', 9236),
    ('27063689', 'VeteranHarry', 12594),
    ('31883069', 'Zylush', 15200),
    ('416016021', 'YogCon', 15297),
    ('141902679', 'thespiffingbrit', 15654),
    ('38180017', 'Sherlock_Hulmes', 15681),
    ('26574506', 'Lalna', 19949),
    ('71290568', 'Leoz', 22384),
    ('22168131', 'Rythian', 23987),
    ('38167015', 'Ravs_', 26536),
    ('197603698', 'highrollersdnd', 29505),
    ('62568743', 'SquidGame', 30173),
    ('87245015', 'Geestargames', 30608),
    ('46969360', 'Mousie', 31688),
    ('219068259', 'AngoryTom', 36418),
    ('21069037', 'simonhoneydew', 36765),
    ('21615575', 'Nilesy', 38342),
    ('38051463', 'ZoeyProasheck', 46937),
    ('113954840', 'bouphe', 47124),
    ('42314834', 'TheRambler146', 47976),
    ('91990032', 'ispuuuv', 48695),
    ('43903804', 'NanoKim', 48718),
    ('37569443', 'Rimmy', 54014),
    ('52172280', 'bokoen', 89693),
    ('19309473', 'Pyrionflax', 128213),
    ('24070690', 'Pedguin', 151325),
    ('21945983', 'HatFilms', 155724),
    ('12131870', 'InTheLittleWood', 209459),
    ('26538483', 'sips_', 428204),
    ('20786541', 'Yogscast', 961975)
]


def get_total_follower_count(cred: TwitchCredentials) -> [(str, str, int)]:
    return list(
        sorted(
            map(lambda x: (x[0],
                           x[1],
                           get_follower_count(cred=cred, twitch_id=x[0])),
                channel_list), key=lambda tup: tup[2],
            reverse=True
        )
    )


def get_balanced_channel_lists(cred: TwitchCredentials, num_of_processes: int, max_follower=None) -> [
    [(str, str, int)]]:
    result: [(str, str, int)] = get_total_follower_count(cred)
    if max_follower is not None:
        result = list(filter(lambda c: c[2] <= max_follower, get_total_follower_count(cred)))

    return get_balanced_channel_lists_from_list(result, num_of_processes)


def get_balanced_channel_lists_2(cred: TwitchCredentials, num_of_processes: int, max_follower=None) -> [
    [(str, str, int)]]:
    result: [(str, str, int)] = get_total_follower_count(cred)
    if max_follower is not None:
        result = list(filter(lambda c: c[2] <= max_follower, get_total_follower_count(cred)))

    return get_balanced_channel_lists_from_list_2(result, num_of_processes)


def get_balanced_channel_lists_from_list(l: [(str, str, int)], num_of_processes: int) -> [[(str, str, int)]]:
    total = sum(map(lambda x: x[2], l))
    max_per_sub_list = total // num_of_processes
    sub_lists: [[(str, str, int)]] = [[] for _ in range(num_of_processes)]
    for channel in l:
        for i in range(num_of_processes):
            if sum(map(lambda x: x[2], sub_lists[i])) <= max_per_sub_list:
                sub_lists[i].append(channel)
                break
    return sub_lists


def test():
    cred = get_cred(client_id=clientID, secret=secret)
    l = get_balanced_channel_lists(cred, 4, 50000)
    for s in l:
        print(s)
        print(f'{sum(map(lambda c: c[2], s))}, {len(s)}')
    pass


def total(lst: [[(str, str, str)]]):
    return sum(map(lambda sub: sum(map(lambda c: c[2], sub)), lst))


def score(lst: [[(str, str, str)]]):
    t = total(lst)
    return sum(map(lambda sub: abs(sum(map(lambda c: c[2], sub)) - (t // len(lst))), lst))


def __move(lst: [[]], f: int, t: int, p: int):
    if t < 0 or f < 0 or t >= len(lst) or f >= len(lst):
        return lst
    if p < 0 or p >= len(lst[f]):
        return lst
    r = []
    for i, l in enumerate(lst):
        if i == f:
            r.append(lst[f][:p] + lst[f][p + 1:])
        elif i == t:
            r.append(lst[t] + [lst[f][p]])
        else:
            r.append(l)
    return r


def best_move(lst: [[]]):
    p = len(lst)
    init_list_temp = lst
    for f in range(p):
        for t in range(p):
            for p in range(sum(map(lambda sub: len(sub), lst))):
                temp = __move(init_list_temp, f, t, p)
                if score(temp) < score(init_list_temp) and total(temp) == total(init_list_temp):
                    init_list_temp = temp
    return init_list_temp


def get_balanced_channel_lists_from_list_2(l: [(str, str, int)], num_of_processes: int) -> [[(str, str, int)]]:
    init_list = [l] + [[] for _ in range(num_of_processes - 1)]
    for i in range(100):
        temp = best_move(init_list)
        if score(temp) == score(init_list):
            break
        if score(temp) < score(init_list) and total(temp) == total(init_list):
            init_list = temp
    return list(map(lambda s: list(sorted(s, key=lambda c: c[2])), init_list))


if __name__ == '__main__':
    cred = get_cred(client_id=clientID, secret=secret)
    channel = get_total_follower_count(cred)
    n = 4
    a = get_balanced_channel_lists_from_list(channel, n)
    b = get_balanced_channel_lists_from_list_2(channel, n)

    for l in a:
        print(f'{sum(map(lambda c: c[2], l))}, {abs(sum(map(lambda c: c[2], l)) - total(a) // len(a))}, {len(l)}')
    print('-')
    print(total(a))
    print(score(a))
    print('------')
    for l in b:
        print(l)
        print(f'{sum(map(lambda c: c[2], l))}, {abs(sum(map(lambda c: c[2], l)) - total(b) // len(b))}, {len(l)}')
    print('-')
    print(total(b))
    print(score(b))

    pass
