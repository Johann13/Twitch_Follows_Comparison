from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from twitch_api import TwitchFollowRelation

twitch_id = '38051463'


def __create_figure(twitch_id: str):
    f = open(f"{twitch_id}.txt", "r", encoding='utf-16')
    follows = list(map(lambda l: TwitchFollowRelation.from_line(l), f))
    dates = list(map(lambda f: f.get_day(), follows))
    uniq_dates = set(dates)
    print(len(dates))
    print(len(uniq_dates))
    data = list(sorted(map(lambda u: (u, dates.count(u), datetime.strptime(u, '%Y-%m-%d').weekday()), uniq_dates),
                       key=lambda tup: tup[0]))
    weekdays = [sum(map(lambda d: d[1], filter(lambda d: d[2] == x, data))) for x in range(7)]

    fig1 = go.Scatter(x=list(map(lambda d: d[0], data)), y=list(map(lambda d: d[1], data)))
    fig2 = go.Bar(x=['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], y=weekdays)
    fig = make_subplots(rows=1, cols=2)
    fig.add_trace(fig1, row=1, col=1)
    fig.add_trace(fig2, row=1, col=2)
    fig.show()
    return fig1, fig2


if __name__ == '__main__':
    __create_figure(twitch_id)

    pass
