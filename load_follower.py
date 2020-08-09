from multiprocessing import Process

from follower_count import get_total_follower_count
from load_follower_from_file import load_follower_from_file
from twitch_api import get_cred, get_twitch_follower_relation, TwitchFollowRelation, TwitchCredentials
from twitch_cred import cred_list


def load_follower_and_write_to_file(cred: TwitchCredentials, twitch_id: str, max_results=None):
    follows_load = load_follower_from_file(twitch_id)
    if len(follows_load) == 0:
        cursor = ''
    else:
        cursor = follows_load[-1].page
    follows: [TwitchFollowRelation] = get_twitch_follower_relation(cred=cred,
                                                                   twitch_id=twitch_id,
                                                                   cursor=cursor,
                                                                   max_results=max_results)

    with open(f"data/{twitch_id}.txt", "a", encoding='utf-16') as file:
        for index, follow in enumerate(follows):
            if follow not in follows_load:
                s = follow.to_string().replace('\n', '')
                if len(follows_load) == 0:
                    file.write(str(index).zfill(7) + ' ' + s)
                else:
                    file.write(str(index + follows_load[-1].index + 1).zfill(7) + ' ' + s)
                file.write('\n')
            else:
                print(f'DUPLICATE {follow}')


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def channel_process(cred: TwitchCredentials, channel: (str, str, int)):
    twitch_id = channel[0]
    channel_name = channel[1]
    channel_follower_count = channel[2]
    print(f'Channel {channel_name}')
    try:
        f = open(f"data/{twitch_id}.txt", "a", encoding='utf-16')
        f.close()
    except FileExistsError:
        print('file already exists')
    finally:
        follows_load = load_follower_from_file(twitch_id)
        if channel_follower_count - len(follows_load) <= 0:
            print(f'Skip {channel_name}')
            return
        m = ((channel_follower_count - len(follows_load)) // 1000) + 1
        for i in range(m):
            print(f'{channel_name}: {i + 1}/{m}')
            load_follower_and_write_to_file(cred, twitch_id, max_results=1000)
        print(f'Done {channel_name}')


def channel_group_process(cred: TwitchCredentials, channel_lst: [(str, str, int)]):
    for c in channel_lst:
        channel_process(cred, c)
    pass


if __name__ == '__main__':
    creds = list(map(lambda c: get_cred(client_id=c[0], secret=c[1]), cred_list))

    channel_list = list(filter(lambda x: 50000 < x[2], get_total_follower_count(creds[0])))
    sub_lsts = [[], [], [], []]
    for i, c in enumerate(channel_list):
        sub_lsts[i % 4].append(c)

    processes: [Process] = []
    for i, sub_lst in enumerate(sub_lsts):
        p = Process(
            target=channel_group_process,
            args=(
                creds[i],
                sub_lst
            )
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
