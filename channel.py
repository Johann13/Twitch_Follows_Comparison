# TODO Provide channel ids and names
# list of channel (id,nam)
channel_list: [(str, str)] = []

# converting the list to a map
channel_map: {str: str} = {c[0]: c[1] for c in channel_list}

# list of channel ids
channel_ids = list(map(lambda c: c[0], channel_list))

# id of the channel you want to compare two
main_channel_id: str = ''
