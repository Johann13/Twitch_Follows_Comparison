from load_follower_from_file import load_follower_from_file
from follower_count import get_total_follower_count
from twitch_api import get_cred
from twitch_cred import clientID, secret
import plotly.graph_objects as go

if __name__ == '__main__':
    cred = get_cred(client_id=clientID, secret=secret)
    result: [(str, str, int)] = get_total_follower_count(cred)
    # result = list(filter(lambda c: c[2] <= 100000, result))
    names = list(map(lambda c: c[1], result))
    heatmap: [[int]] = []
    m: {str: []} = {}
    for c in result:
        follower = load_follower_from_file(c[0])
        ids: {str} = set(map(lambda f: f.twitch_id, follower))
        m[c[0]] = ids

    for c1 in result:
        sub = []
        ids1: {str} = m[c1[0]]
        for c2 in result:
            if c1[0] == c2[0]:
                sub.append(None)
                continue
            ids2: {str} = m[c2[0]]
            inter = ids1.intersection(ids2)
            union = ids1.union(ids2)
            sub.append(round(len(inter) / len(union) * 100, 2))
            print(
                f'{c1[1]}, {len(ids1)} - {c2[1]}, {len(ids2)} = {len(union)}, {len(inter)}, ({round(len(inter) / len(union) * 100, 2)})')
        heatmap.append(sub)

    print(heatmap)
    with open('data/graph/heatmap.txt', 'w+') as h:
        h.write(f'{heatmap}')
    fig = go.Figure(data=go.Heatmap(
        z=heatmap,
        x=names,
        y=names,
    ))
    fig.show()

    pass
