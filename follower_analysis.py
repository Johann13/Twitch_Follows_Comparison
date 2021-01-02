import csv
import multiprocessing
import os
import time
from typing import Set

import twitch_api
import twitch_cred
import write_twitch_csv
from channel import channel_list
from models import SimpleFollow, TwitchCredentials


def write_follow_ids_to_csv():
    follow_ids: Set[str] = set()

    for c in channel_list:
        channel_id, channel_name = c
        follower_list: [SimpleFollow] = write_twitch_csv.load_twitch_follows_from_csv(channel_id)
        for follow in follower_list:
            follow_ids.add(follow.twitch_id)
    print(len(follow_ids))

    with open('data/follows.csv', 'w', newline='') as csv_file:
        w = csv.writer(csv_file,
                       delimiter=',',
                       quotechar='|',
                       quoting=csv.QUOTE_MINIMAL)
        for follow_id in follow_ids:
            w.writerow([follow_id])
    pass


def load_follows_from_csv() -> [str]:
    return load_ids_from_csv('data/follows.csv')


def load_ids_from_csv(file_name: str) -> [str]:
    follows = []
    if not os.path.exists(file_name):
        return follows
    csv_file = open(file_name, 'r', newline='')
    r = csv.reader(csv_file)
    follows = [l[0] for l in r][1:]
    csv_file.close()
    return follows


def load_other_follows_and_write_to_csv(follow_ids: [str], file_name: str, p_id: int, cred: TwitchCredentials):
    other_channel_ids: [] = []
    len_follow_ids = len(follow_ids)
    start_time = time.time()
    for i, follow_id in enumerate(follow_ids):
        channel_ids = twitch_api.get_channel_follows_ids(follow_id, cred)
        for channel_id in channel_ids:
            other_channel_ids.append(channel_id)
        if i % 1000 == 0 and i > 0:
            end_time = time.time()
            print(f'{p_id}: {i}/{len_follow_ids}, {end_time - start_time}s')
        pass

    with open(f'data/{file_name}', 'w', newline='') as csv_file:
        w = csv.writer(csv_file,
                       delimiter=',',
                       quotechar='|',
                       quoting=csv.QUOTE_MINIMAL)
        for channel_id in other_channel_ids:
            w.writerow([channel_id])
    pass


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == '__main__':
    # write_follow_ids_to_csv()
    follow_ids: [str] = load_follows_from_csv()
    follow_ids_chunks = chunks(follow_ids, 50000)
    ps: [multiprocessing.Process] = []
    creds = list(map(lambda c: twitch_api.get_cred(c[0], c[1]), twitch_cred.cred_list))

    for i, l in enumerate(follow_ids_chunks):
        p = multiprocessing.Process(
            target=load_other_follows_and_write_to_csv,
            args=(l, f'follow_file_{i}.csv', i, creds[i % len(creds)])
        )
        ps.append(p)

    for p in ps:
        p.start()
    for p in ps:
        p.join()

    # load_other_follows_and_write_to_csv(follow_ids)
