import datetime
import plotly.express as px

from channel import channel_list, todo
from twitch_api import get_cred, get_twitch_follower_relation, TwitchFollowRelation
from twitch_cred import clientID, secret


def load_follower_and_write_to_file(twitch_id: str):
    cred = get_cred(client_id=clientID, secret=secret)
    resp: [TwitchFollowRelation] = get_twitch_follower_relation(cred=cred, twitch_id=twitch_id)
    f = open(f"data/{twitch_id}.txt", "a", encoding='utf-16')
    f2 = open(f"data/names_{twitch_id}.txt", "a", encoding='utf-16')
    for i, r in enumerate(resp):
        f.write(str(i).zfill(7) + ' ' + r.to_string())
        f2.write(str(i).zfill(7) + ' ' + r.from_user.to_string())
        f.write('\n')
        f2.write('\n')
    f.close()
    f2.close()


if __name__ == '__main__':
    for channel in todo:
        load_follower_and_write_to_file(channel[0])
