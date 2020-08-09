from channel import channel_list
from twitch_api import get_cred, get_follower_count, TwitchCredentials
from twitch_cred import clientID, secret


def get_total_follower_count(cred: TwitchCredentials) -> [(str, str, int)]:
    return list(
        sorted(
            map(lambda x: (x[0],
                           x[1],
                           get_follower_count(cred=cred, twitch_id=x[0])),
                channel_list), key=lambda tup: tup[2]
        )
    )


if __name__ == '__main__':
    cred = get_cred(client_id=clientID, secret=secret)
    result = get_total_follower_count(cred)
    for r in result:
        print(r)
