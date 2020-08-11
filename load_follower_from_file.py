from twitch_api import TwitchFollowRelation


def load_follower_from_file(path: str) -> [TwitchFollowRelation]:
    f = open(path, "r+", encoding='utf-16')
    follows = list(map(lambda l: TwitchFollowRelation.from_line(l),
                       filter(lambda l: l != '\n', f)))
    f.close()
    return follows
