from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from channel import channel_list
from follower_count import get_total_follower_count
from load_follower_from_file import load_follower_relation_from_file
from twitch_api import get_cred
from twitch_cred import clientID, secret


def __create_channel_follower_time_line(c: (str, str, int)):
    twitch_id, twitch_name, count = c
    follows = load_follower_relation_from_file(f"data/follower/{twitch_id}.txt")
    dates = list(map(lambda f: f.get_day(), follows))
    uniq_dates = set(dates)

    data = list(sorted(map(lambda u: (u, dates.count(u)), uniq_dates),
                       key=lambda tup: tup[0]))
    with open(f'data/timeline/{twitch_id}.txt', 'w+') as f:
        f.write(f'{data}')


def __create_figure(c: (str, str, int)):
    twitch_id, twitch_name, count = c
    follows = load_follower_relation_from_file(f"data/follower/{twitch_id}.txt")
    dates = list(map(lambda f: f.get_day(), follows))
    uniq_dates = set(dates)

    data = list(sorted(map(lambda u: (u, dates.count(u), datetime.strptime(u, '%Y-%m-%d').weekday()), uniq_dates),
                       key=lambda tup: tup[0]))
    weekdays = [sum(map(lambda d: d[1], filter(lambda d: d[2] == x, data))) for x in range(7)]

    fig1 = go.Scatter(x=list(map(lambda d: d[0], data)), y=list(map(lambda d: d[1], data)))
    fig2 = go.Bar(x=['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], y=weekdays)

    return fig1, fig2


if __name__ == '__main__':
    cred = get_cred(client_id=clientID, secret=secret)
    lst = list(filter(lambda c: 6000 < c[2] < 20000, get_total_follower_count(cred)))

    for i, c in enumerate(lst):
        __create_channel_follower_time_line(c)
    # fig.add_trace(fig1, row=i + 1, col=2)
    pass
