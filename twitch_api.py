from datetime import datetime
import time
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


def twitch_api_get(
        twitch_url: str,
        cred: TwitchCredentials,
        params: {str: str}) -> TwitchResponse:
    r""""""
    headers = {
        'Client-ID': cred.client_id,
        'Authorization': 'Bearer ' + cred.token
    }
    response = requests.get(twitch_url, headers=headers, params=params)
    return TwitchResponse(response)


def twitch_api_post(
        twitch_url: str,
        cred: TwitchCredentials,
        params: {str: str}) -> TwitchResponse:
    r""""""
    headers = {
        'Client-ID': cred.client_id,
        'Authorization': 'Bearer ' + cred.token
    }
    response = requests.post(twitch_url, headers=headers, params=params)
    return TwitchResponse(response)


def __get_twitch_follower_relation(cred: TwitchCredentials, twitch_id: str, page=None) -> (
        [TwitchFollowRelation], str, int):
    if page is None:
        resp = twitch_api_get(
            twitch_url='https://api.twitch.tv/helix/users/follows',
            cred=cred,
            params={'to_id': twitch_id, 'first': 100},
        )
    else:
        resp = twitch_api_get(
            twitch_url='https://api.twitch.tv/helix/users/follows',
            cred=cred,
            params={'to_id': twitch_id, 'first': 100, 'after': page},
        )
    if resp.should_sleep:
        print('sleep')
        time.sleep(32)
        return __get_twitch_follower_relation(cred=cred, twitch_id=twitch_id, page=page)
    data = resp.json['data']
    cursor = None
    if 'cursor' in resp.json['pagination']:
        cursor = resp.json['pagination']['cursor']

    return list(map(lambda d: TwitchFollowRelation.from_api(d, cursor), data)), cursor, resp.json['total']


def get_twitch_follower_relation(cred: TwitchCredentials, twitch_id: str, max_results=None, cursor='') \
        -> [TwitchFollowRelation]:
    total: int = 0
    result: [TwitchFollowRelation] = []
    while len(result) < total or len(result) == 0:
        if cursor is None:
            break
        else:
            cursor = cursor.replace('\n', '')
        if max_results is not None:
            if len(result) >= max_results:
                break
        resp = __get_twitch_follower_relation(cred=cred, twitch_id=twitch_id, page=cursor)
        total = resp[2]
        cursor = resp[1]
        result += resp[0]

    return result


def get_follower_count(cred: TwitchCredentials, twitch_id: str, ) -> int:
    resp = twitch_api_get(
        twitch_url='https://api.twitch.tv/helix/users/follows',
        cred=cred,
        params={'to_id': twitch_id, 'first': 1},
    )
    return resp.json['total']


'''
Gets the follower recursively of a channel by twitch id
This can be changed to use the twitch name as well instead of the id
If the bearer_toke is not provided the limit for API Requests is 30 per minute
If provided it is 800 per minute
'''


def get_channel_follower(twitch_id: str,
                         client_id: str,
                         user_count: int,
                         page: str = None,
                         prev_result: {} = None,
                         sleep=6,
                         first=100,
                         bearer_token=None,
                         print_state=False,
                         print_error=True,
                         print_headers=False) -> {}:
    if print_state:
        print('run get_channel_follower for ' + str(twitch_id))
    if prev_result is not None:
        if len(prev_result['data']) >= user_count:
            return prev_result
    else:
        prev_result = {
            'total': 0,
            'data': [],
            'page': ''
        }

    twitch_url = 'https://api.twitch.tv/helix/users/follows'
    headers = {
        'Client-ID': client_id,
    }

    if bearer_token is not None:
        headers['Authorization'] = 'Bearer ' + bearer_token
    params = {
        'to_id': twitch_id,
        'first': first,
    }
    if page is not None:
        params['after'] = page
    response = requests.get(twitch_url, headers=headers, params=params)
    secs = int(round(time.time()))
    if print_headers:
        print(response.headers)
    ratelimit_reset = int(response.headers['ratelimit-reset'])
    diff = ratelimit_reset - secs
    ratelimit_remaining = int(response.headers['ratelimit-remaining'])
    ratelimit_limit = int(response.headers['ratelimit-limit'])
    if print_state:
        print((ratelimit_reset, ratelimit_remaining, ratelimit_limit))
    if ratelimit_remaining <= 0:
        print('sleep cause of ratelimit-remaining')
        print('sleep ' + str(diff) + ' sec')
        print(client_id)
        time.sleep(diff)
    json = response.json()
    if 'error' in json:
        if json['status'] == 429:
            if print_error:
                print(client_id)
                print('error for ' + str(twitch_id) + ', wait ' + str(sleep) + ' seconds')
            return get_channel_follower(twitch_id, client_id, user_count, page, prev_result,
                                        sleep=sleep + 2,
                                        bearer_token=bearer_token,
                                        print_state=print_state,
                                        print_error=print_error,
                                        print_headers=print_headers)

    page = None
    if 'pagination' in json:
        if 'cursor' in json['pagination']:
            page = json['pagination']['cursor']
    data: [] = json['data']
    total = json['total']
    prev_result['total'] = total
    if print_state:
        print('found a total of ' + str(json['total']) + ' follower for channel ' + str(twitch_id))
    prev_result['page'] = page
    for user_data in data:
        prev_result['data'].append({
            'name': user_data['from_name'],
            'id': user_data['from_id'],
            'followed_at': user_data['followed_at']
        })
    if page is None or total <= len(prev_result['data']):
        return prev_result
    return get_channel_follower(twitch_id, client_id, user_count, page, prev_result,
                                sleep=sleep + 2,
                                bearer_token=bearer_token,
                                print_state=print_state,
                                print_error=print_error,
                                print_headers=print_headers)


'''
Gets the follows recursively of a user by twitch id
This can be changed to use the twitch name as well instead of the id
If the bearer_toke is not provided the limit for API Requests is 30 per minute
If provided it is 800 per minute
'''


def get_channel_follows(twitch_id: str,
                        client_id: str,
                        page: str = None,
                        prev_result: {} = None,
                        sleep=6,
                        bearer_token=None,
                        print_state=False,
                        print_error=True,
                        print_headers=False) -> {}:
    if print_state:
        print('run get_channel_follower for ' + str(twitch_id))
    if prev_result is None:
        prev_result = {
            'total': 0,
            'data': [],
            'page': ''
        }

    twitch_url = 'https://api.twitch.tv/helix/users/follows'
    headers = {
        'Client-ID': client_id,
    }
    if bearer_token is not None:
        headers['Authorization'] = 'Bearer ' + bearer_token
    params = {
        'from_id': twitch_id,
        'first': 100,
    }
    if page is not None:
        params['after'] = page
    response = requests.get(twitch_url, headers=headers, params=params)

    if print_headers:
        print(response.headers)
    secs = int(round(time.time()))
    ratelimit_reset = int(response.headers['ratelimit-reset'])
    diff = ratelimit_reset - secs
    ratelimit_remaining = int(response.headers['ratelimit-remaining'])
    ratelimit_limit = int(response.headers['ratelimit-limit'])
    if print_state:
        print('ratelimit_remaining: ' + str(ratelimit_remaining) + ', ' + str(client_id))
    if ratelimit_remaining <= 0:
        print('sleep cause of ratelimit-remaining')
        print('sleep ' + str(diff) + ' sec')
        print('client_id:' + client_id)
        print('bearer_token:' + str(bearer_token))
        time.sleep(diff)
    json = response.json()
    if 'error' in json:
        if json['status'] == 429:
            if print_error:
                print(client_id)
                print('error for ' + str(twitch_id) + ', wait ' + str(sleep) + ' seconds')
            return get_channel_follows(twitch_id, client_id, page,
                                       prev_result=prev_result,
                                       sleep=sleep * 2,
                                       bearer_token=bearer_token,
                                       print_state=print_state,
                                       print_error=print_error,
                                       print_headers=print_headers)

    page = None
    if 'pagination' in json:
        if 'cursor' in json['pagination']:
            page = json['pagination']['cursor']
    data: [] = json['data']
    total = json['total']
    prev_result['total'] = total
    if print_state:
        print('found a total of ' + str(json['total']) + ' follower for channel ' + str(twitch_id))
    prev_result['page'] = page
    for user_data in data:
        prev_result['data'].append({
            'name': user_data['to_name'],
            'id': user_data['to_id'],
            'followed_at': user_data['followed_at']
        })
    if page is None or total <= len(prev_result['data']):
        return prev_result
    return get_channel_follows(twitch_id, client_id, page, prev_result,
                               sleep=sleep + 2,
                               bearer_token=bearer_token,
                               print_state=print_state,
                               print_error=print_error,
                               print_headers=print_headers)


'''
Get the bearer token
'''


def __get_bearer_token(client_id: str, secret: str) -> {}:
    twitch_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post(twitch_url, params=params)
    return response.json()


def get_cred(client_id: str, secret: str) -> TwitchCredentials:
    r"""Returns a tuple of client id and token.
    :param client_id application id, which can be found in the twitch dev console
    :param secret application secret, which can be found in the twitch dev console
    do not share this with anyone
    :return TwitchCredentials
    :rtype TwitchCredentials
    """
    token = __get_bearer_token(client_id, secret)['access_token']
    return TwitchCredentials(client_id, secret, token)
