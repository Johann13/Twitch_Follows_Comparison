import os
from multiprocessing import Process

from follower_count import get_balanced_channel_lists_2, get_total_follower_count
from load_follower_from_file import load_follower_from_file
from twitch_api import get_cred, get_twitch_follower_relation, TwitchFollowRelation, TwitchCredentials
from twitch_cred import cred_list, clientID, secret


def channel_process(cred: TwitchCredentials, channel: (str, str, int), max_results=1000):
    twitch_id, channel_name, channel_follower_count = channel
    if not os.path.exists(f'data/follower/{twitch_id}.txt'):
        open(f'data/follower/{twitch_id}.txt', 'w').close()
    follower = load_follower_from_file(f'data/follower/{twitch_id}.txt')
    current_count = len(follower)
    if len(follower) >= channel_follower_count:
        print(f'Skip {channel_name}')
        return
    else:
        print(f'{len(follower)} in file, {channel_follower_count} online')
    if len(follower) > 0:
        print(f'Already loaded {current_count}')
        cursor = follower[-1].page
    else:
        cursor = ''

    print(f'Starting {twitch_id} - {channel_name} - {channel_follower_count}')
    while len(follower) < channel_follower_count:

        print(f'Load Data - {channel_name} - {cursor}')
        result: [TwitchFollowRelation] = get_twitch_follower_relation(
            cred=cred,
            twitch_id=twitch_id,
            cursor=cursor,
            max_results=max_results
        )

        if len(result) == 0:
            print(f'No more follows found - {channel_name}')
            break

        print(f'Write File - {channel_name}')
        data = ''
        for i, follow in enumerate(result):
            data += f'{i + current_count} {follow.to_string()}\n'

        with open(f'data/follower/{twitch_id}.txt', 'a+', encoding='utf-16') as file:
            file.write(data)
        follower += result
        last: TwitchFollowRelation = result[-1]
        cursor = last.page
        print(f'Done - {channel_name} {len(follower)}/{channel_follower_count}')

    print(f'Done {channel_name} {twitch_id}')

    pass


def multi_channel_process(cred: TwitchCredentials, channel_list: [(str, str, int)], max_results=1000):
    for c in channel_list:
        channel_process(cred, c, max_results=max_results)
    print('multi_channel_process done')


def load():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/follower'):
        os.makedirs('data/follower')
    num_of_processes = 4
    print('Loading Creds')
    creds = list(map(lambda c: get_cred(client_id=c[0], secret=c[1]), cred_list))
    cred = creds[0]  # get_cred(client_id=clientID, secret=secret)
    print('Loaded Creds')

    print('Loading Channel')
    sub_lists = get_balanced_channel_lists_2(cred, num_of_processes)
    print('Loaded Channel')
    print('Init Processes')
    processes = []
    for i, sub_list in enumerate(sub_lists):
        p = Process(
            target=multi_channel_process,
            args=(
                creds[i],
                sub_list
            )
        )
        processes.append(p)

    print('Start Processes')
    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    load()
    pass
