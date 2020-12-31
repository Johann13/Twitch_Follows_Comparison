import time
from datetime import datetime

import requests


class TwitchCredentials:
    def __init__(self, client_id, secret, token):
        self.client_id = client_id
        self.secret = secret
        self.token = token
        pass

    def __str__(self):
        return self.client_id

    def __repr__(self):
        return f'TwitchCredentials({self.client_id})'


class TwitchResponse:

    def __init__(self, response: requests.Response):
        secs = int(round(time.time()))
        self.json = response.json()
        self.rate_limit_reset = int(response.headers['ratelimit-reset'])
        self.diff = self.rate_limit_reset - secs
        self.rate_limit_remaining = int(response.headers['ratelimit-remaining'])
        self.rate_limit_limit = int(response.headers['ratelimit-limit'])
        self.should_sleep = self.rate_limit_remaining <= 0
        self.has_error = 'error' in self.json
        if 'error' in self.json:
            self.error = self.json['error']
        else:
            self.error = None

    pass

    def __repr__(self):
        return f'TwitchResponse({self.json})'

    def __str__(self):
        return f'{self.json}'


class TwitchUser:
    def __init__(self, twitch_id, twitch_name):
        self.twitch_id = twitch_id
        self.twitch_name = twitch_name

    def __repr__(self):
        return f'TwitchUser({self.twitch_id},{self.twitch_name})'

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return f'{self.twitch_id} {self.twitch_name}'


class SimpleFollow:
    def __init__(self, twitch_id: str, year: str, month: str, day: str):
        self.twitch_id = twitch_id
        self.y = year
        self.m = month
        self.d = day
        pass

    @classmethod
    def from_line(cls, line: str):
        words = list(line.split(' '))
        return cls(words[0], words[1])

    def get_date(self):
        return datetime.strptime(self.date, '%Y-%m-%d')

    def get_day(self):
        date = self.get_date()
        return f'{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}'


class TwitchFollowRelation:

    def __init__(self, index: int, from_id: str, from_name: str,
                 to_id: str, to_name: str,
                 followed_at: str, page: str):
        self.index = index
        self.from_user = TwitchUser(from_id, from_name)
        self.to_user = TwitchUser(to_id, to_name)
        self.from_id = from_id
        self.from_name = from_name
        self.to_id = to_id
        self.to_name = to_name
        self.followed_at = followed_at
        s = self.followed_at
        s = s.split('T')[0]
        l = s.split('-')
        self.y = l[0]
        self.m = l[1]
        self.d = l[2]

        self.page = page
        pass

    @classmethod
    def from_api(cls, data: {str: str}, page: str):
        from_id = data['from_id']
        from_name = data['from_name']
        to_id = data['to_id']
        to_name = data['to_name']
        followed_at = data['followed_at']
        page = page
        return cls(0, from_id, from_name, to_id, to_name, followed_at, page)

    @classmethod
    def from_line(cls, line: str):
        words = list(map(lambda s: s.replace(' ', ''), line.split(' ')))
        if len(words) > 7:
            words = list(filter(lambda s: s != '', words))
        index = int(words[0])
        from_id = words[1].replace('\n', '')
        from_name = words[2].replace('\n', '')
        to_id = words[3].replace('\n', '')
        to_name = words[4].replace('\n', '')
        followed_at = words[5].replace('\n', '')
        if len(words) == 7:
            page = words[6].replace('\n', '')
        else:
            page = None
        return cls(index, from_id, from_name, to_id, to_name, followed_at, page)

    def get_date(self):
        return datetime.strptime(self.followed_at, '%Y-%m-%dT%H:%M:%SZ')

    def get_day(self):
        date = self.get_date()
        return f'{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}'

    def __repr__(self):
        return f'TwitchFollowRelation({self.from_name},{self.to_name})'

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return f'{self.from_id} {self.from_name} {self.to_id} {self.to_name} {self.followed_at} {self.page}'

    def __eq__(self, other):
        if other is TwitchFollowRelation:
            return self.from_id == other.from_id and self.to_id == other.to_id
        return False

    def __hash__(self):
        return int(f'{self.from_id}{self.to_id}')
