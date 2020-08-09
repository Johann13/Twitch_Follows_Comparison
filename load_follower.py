import datetime
import plotly.express as px

from channel import channel_list, todo
from load_follower_from_file import load_follower_from_file
from twitch_api import get_cred, get_twitch_follower_relation, TwitchFollowRelation
from twitch_cred import clientID, secret


def load_follower_and_write_to_file(twitch_id: str, max_results=None):
    follows_load = load_follower_from_file(twitch_id)
    if len(follows_load) == 0:
        cursor = ''
    else:
        cursor = follows_load[-1].page
    print(f'follows: {len(follows_load)}')
    print(f'loaded cursor: {cursor}')

    cred = get_cred(client_id=clientID, secret=secret)
    follows: [TwitchFollowRelation] = get_twitch_follower_relation(cred=cred,
                                                                   twitch_id=twitch_id,
                                                                   cursor=cursor,
                                                                   max_results=max_results)

    with open(f"data/{twitch_id}.csv", "a", encoding='utf-16') as file:
        for index, follow in enumerate(follows):
            if follow not in follows_load:
                s = follow.to_string().replace('\n', '').replace(' ',';')
                print(s)
                if len(follows_load) == 0:
                    file.write(str(index).zfill(7) + ';' + s)
                else:
                    file.write(str(index + follows_load[-1].index + 1).zfill(7) + ';' + s)
                file.write('\n')
            else:
                print(f'DUPLICATE {follow}')


def remove_empty_lines(twitch_id: str):
    with open(f'data/{twitch_id}.txt', encoding='utf-16') as filehandle:
        lines = filehandle.readlines()
        print(len(lines))
        lines = list(set(filter(lambda x: x.strip(), lines)))
        print(len(lines))
        follows = list(map(lambda l: TwitchFollowRelation.from_line(l), lines))
        print(len(follows))
        follows = list(set(map(lambda l: TwitchFollowRelation.from_line(l), lines)))
        print(len(follows))


if __name__ == '__main__':

    for channel in todo:
        twitch_id = channel[0]
        try:
            f = open(f"data/{twitch_id}.csv", "a", encoding='utf-16')
            f.close()
        except FileExistsError:
            print('file already exists')
        finally:
            for i in range(4):
                print(f'---{i + 1}/{4}---')
                load_follower_and_write_to_file(twitch_id, max_results=200)
                follows_load = load_follower_from_file(twitch_id)
                print(len(follows_load))
