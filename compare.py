import csv

import write_twitch_csv
from channel import channel_list
from models import SimpleFollow


def compare(channel_list: (str, str)):
    header = ['']
    follow_map: {str: [SimpleFollow]} = {}
    for c in channel_list:
        header.append(c[1])

    for c in channel_list:
        channel_id, channel_name = c
        follow_map[channel_id] = write_twitch_csv.load_twitch_follows_from_csv(channel_id)

    directory = f'data/compare.csv'
    directory2 = f'data/compare2.csv'
    csv_file = open(directory, 'w', newline='')
    csv_file2 = open(directory2, 'w', newline='')
    w = csv.writer(csv_file,
                   delimiter=',',
                   quotechar='|',
                   quoting=csv.QUOTE_MINIMAL)
    w.writerow(header)
    w2 = csv.writer(csv_file2,
                    delimiter=',',
                    quotechar='|',
                    quoting=csv.QUOTE_MINIMAL)
    w2.writerow(header)

    for channel1 in channel_list:
        channel1_id, channel1_name = channel1
        follows1: [SimpleFollow] = follow_map[channel1_id]
        row = []
        row2 = []
        row.append(channel1_name)
        row2.append(channel1_name)
        if len(follows1) <= 0:
            for _ in channel_list:
                row.append('-')
                row2.append('-')
            continue

        for channel2 in channel_list:
            channel2_id, channel2_name = channel2
            print(f'compare {channel1_name} - {channel2_name}')
            if channel1_id == channel2_id:
                row.append('-')
                row2.append('-')
                continue
            follows2: [SimpleFollow] = follow_map[channel2_id]
            if len(follows2) <= 0:
                row.append('-')
                row2.append('-')
                continue
            set1: {str} = set(map(lambda f: f.twitch_id, follows1))
            set2: {str} = set(map(lambda f: f.twitch_id, follows2))
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            row.append(len(intersection))
            row2.append("{:.2f}".format((len(follows2) / len(union)) * 100))
            pass
        w.writerow(row)
        w2.writerow(row2)
        pass
    csv_file.close()
    csv_file2.close()
    pass


if __name__ == '__main__':
    compare(channel_list)
