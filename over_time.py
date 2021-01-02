import csv

from channel import channel_list
from models import SimpleFollow
from write_twitch_csv import load_twitch_follows_from_csv


def _data(start_year: int, end_year: int) -> [(str, str)]:
    return [(f'{y}', f'{m}'.rjust(2, '0')) for y in range(start_year, end_year + 1, 1) for m in range(1, 13, 1)]


def _over_time(channel: (str, str)):
    twitch_id, twitch_name = channel
    follows: [SimpleFollow] = load_twitch_follows_from_csv(twitch_id)
    dates: [(str, str)] = _data(2011, 2020)
    return [len(list(filter(lambda f: f.y == y and f.m == m, follows))) for (y, m) in dates]


def growth(channel: [(str, str)]):
    dates: [(str, str)] = _data(2011, 2020)
    header: [str] = [f'{m}.{y}' for (y, m) in dates]
    header.insert(0, '')
    csv_file = open('data/growth.csv', 'w', newline='')
    csv_file2 = open('data/total_over_time.csv', 'w', newline='')
    w = csv.writer(csv_file,
                   delimiter=',',
                   quotechar='|',
                   quoting=csv.QUOTE_MINIMAL)
    w2 = csv.writer(csv_file2,
                    delimiter=',',
                    quotechar='|',
                    quoting=csv.QUOTE_MINIMAL)
    w.writerow(header)
    w2.writerow(header)
    for c in channel:
        timeline = _over_time(c)
        row = [c[1]]
        row2 = [c[1]]
        timeline2 = [sum(timeline[:(i + 1)]) for i in range(len(timeline))]
        for t in timeline:
            row.append(t)
        for t in timeline2:
            row2.append(t)
        w.writerow(row)
        w2.writerow(row2)

    csv_file.close()
    csv_file2.close()
    pass


if __name__ == '__main__':
    growth(channel_list)
