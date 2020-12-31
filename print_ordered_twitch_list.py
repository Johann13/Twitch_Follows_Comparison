from channel import channel_list
from twitch_api import get_cred, get_follower_count
from twitch_cred import secret, clientID

if __name__ == '__main__':
    cred = get_cred(client_id=clientID, secret=secret)
    channel = list(
        sorted(
            map(lambda x: (x[0], x[1], get_follower_count(cred, x[0])),
                channel_list
                ),
            key=lambda x: x[1].upper()
        )
    )

    for c in channel:
        print(c)
