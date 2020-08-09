from twitch_api import TwitchFollowRelation


def load_follower_from_file(twitch_id: str) -> [TwitchFollowRelation]:
    f = open(f"data/{twitch_id}.txt", "r+", encoding='utf-16')
    follows = list(map(lambda l: TwitchFollowRelation.from_line(l),
                       filter(lambda l: l != '\n', f)))
    f.close()
    return follows
