import twitch_api
from models import TwitchCredentials, TwitchFollowRelation
from twitch_cred import cred_list
import os
import csv
import write_twitch_csv
clientId, secret = cred_list[0]
twitch_id = '38051463'

directory = f'data/{twitch_id}'
if not os.path.exists(directory):
    os.makedirs(directory)
cred: TwitchCredentials = twitch_api.get_cred(clientId, secret)
write_twitch_csv.load_follower_and_write_to_csv(twitch_id, cred)

#write_twitch_csv.load_twitch_follows_from_csv(twitch_id)
