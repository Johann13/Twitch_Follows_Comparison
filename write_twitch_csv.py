import csv
import os

import twitch_api
from models import TwitchCredentials, TwitchFollowRelation, SimpleFollow


def load_follower_and_write_to_csv(
        twitch_id: str,
        twitch_name: str,
        cred: TwitchCredentials):
    follower: [TwitchFollowRelation] = twitch_api.get_twitch_follower_relation(cred, twitch_id, twitch_name)
    write_to_csv(twitch_id, follower)
    pass


def write_to_csv(twitch_id: str, follower: [TwitchFollowRelation]):
    directory = f'data/{twitch_id}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f'data/{twitch_id}/{twitch_id}.csv', 'w', newline='') as csv_file:
        w = csv.writer(csv_file,
                       delimiter=',',
                       quotechar='|',
                       quoting=csv.QUOTE_MINIMAL)
        w.writerow(['twitch_id', 'twitch_name', 'year', 'month', 'day'])
        for f in follower:
            w.writerow([f.from_user.twitch_id, f.from_user.twitch_name, f.y, f.m, f.d])


def load_twitch_follows_from_csv(twitch_id: str) -> [SimpleFollow]:
    directory = f'data/{twitch_id}/{twitch_id}.csv'
    follows = []
    if not os.path.exists(directory):
        return follows
    csv_file = open(directory, 'r', newline='')
    r = csv.reader(csv_file)
    follows = [SimpleFollow(l[0], l[2], l[3], l[4]) for l in r][1:]
    csv_file.close()
    return follows
