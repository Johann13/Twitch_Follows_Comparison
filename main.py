import multiprocessing
import time

import total_follower_count
import twitch_api
import twitch_cred
import write_twitch_csv
from models import TwitchCredentials


def process_for_one_channel(channel_list: [(str, str, int)], cred: TwitchCredentials):
    channel_list = list(sorted(channel_list, key=lambda x: x[2], ))
    print(f'process: {channel_list}')
    for channel in channel_list:
        twitch_id, twitch_name, total = channel
        l = write_twitch_csv.load_twitch_follows_from_csv(twitch_id)
        if total > len(l):
            s = time.time()
            print(f'{twitch_name}: start {total}')
            write_twitch_csv.load_follower_and_write_to_csv(twitch_id, twitch_name, cred)
            e = time.time()
            d = int(e - s)
            print(f'{twitch_name} done {d}s')
        else:
            print(f'{twitch_name}: skip {total}')
    pass


def main():
    channel: [(str, str, int)] = total_follower_count.get_local()
    channel_lists: [[(str, str, int)]] = total_follower_count.balance2(channel, 16)
    creds = list(map(lambda c: twitch_api.get_cred(c[0], c[1]), twitch_cred.cred_list))
    ps: [multiprocessing.Process] = []
    for i, sub_list in enumerate(channel_lists):
        if len(sub_list) > 0:
            p = multiprocessing.Process(
                target=process_for_one_channel,
                args=(sub_list, creds[i % len(creds)])
            )
            ps.append(p)

    for p in ps:
        p.start()
    for p in ps:
        p.join()


if __name__ == '__main__':
    # print('FionaRiches:     12%,	25s left,	3s spend')
    # print('Zylush:          7%,     53s left,	4s spend')
    main()
    # cred = twitch_api.get_cred(twitch_cred.clientID, twitch_cred.secret)
    # write_twitch_csv.load_follower_and_write_to_csv('91904368', 'bobawitch', cred)
