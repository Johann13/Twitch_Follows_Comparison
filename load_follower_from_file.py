from twitch_api import TwitchFollowRelation, SimpleFollow


def load_follower_relation_from_file(path: str) -> [TwitchFollowRelation]:
    f = open(path, "r+", encoding='utf-16')
    follows = list(map(lambda l: TwitchFollowRelation.from_line(l),
                       filter(lambda l: l != '\n', f)))
    f.close()
    return follows


def load_follower_from_file(twich_id: str) -> [SimpleFollow]:
    f = open(f'data/follower/{twich_id}.txt', "r")
    follows = list(map(lambda l: SimpleFollow.from_line(l),
                       filter(lambda l: l != '\n', f)))
    f.close()
    return follows
