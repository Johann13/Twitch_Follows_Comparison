import time

import requests

from models import TwitchCredentials, TwitchResponse, TwitchFollowRelation


def twitch_api_get(
        twitch_url: str,
        cred: TwitchCredentials,
        params: {str: str}) -> TwitchResponse:
    """
    Make a get request to the twitch api
    :param twitch_url:
    :param cred:
    :param params:
    :return:
    """
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
    """
    Make a post request to the twitch api
    :param twitch_url:
    :param cred:
    :param params:
    :return:
    """
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
        time.sleep(30)
        return __get_twitch_follower_relation(cred=cred, twitch_id=twitch_id, page=page)
    data = resp.json['data']
    cursor = None
    if 'cursor' in resp.json['pagination']:
        cursor = resp.json['pagination']['cursor']

    return list(map(lambda d: TwitchFollowRelation.from_api(d, cursor), data)), cursor, resp.json['total']


def get_twitch_follower_relation(cred: TwitchCredentials, twitch_id: str, twitch_name: str,
                                 max_results=None, cursor='') \
        -> [TwitchFollowRelation]:
    total: int = 0
    result: [TwitchFollowRelation] = []
    start_time = time.time()
    while len(result) < total or len(result) == 0:
        if cursor is None:
            break
        else:
            cursor = cursor.replace('\n', '')
        if max_results is not None:
            if len(result) >= max_results:
                break
        new_result, cursor, total = __get_twitch_follower_relation(cred=cred, twitch_id=twitch_id, page=cursor)
        result += new_result
        f: int = int((len(result) / total) * 100)
        end_time = time.time()
        diff_time = end_time - start_time

        # print(f'total time = {((diff_time / len(new_result)) * total)}')
        # print(f'needed = {(diff_time / len(new_result)) * len(result)}')

        left = ((diff_time / len(result)) * total) \
               - diff_time

        # if f > 0:
        #    if f % 10 == 0:

        result_len = len(result)
        n = twitch_name.ljust(15, ' ')
        f_str = str(f).rjust(5, ' ')
        left_str = str(int(left)).rjust(5, ' ')
        diff_str = str(int(diff_time)).rjust(5, ' ')
        s = f'{n}|{f_str}%|{left_str}s left|{diff_str}s spend'

        if total <= 5000:
            if result_len % 500 == 0:
                print(s)
        elif total <= 10000:
            if result_len % 1000 == 0:
                print(s)
        elif total <= 25000:
            if result_len % 1500 == 0:
                print(s)
        elif total <= 50000:
            if result_len % 5000 == 0:
                print(s)
        elif total <= 75000:
            if result_len % 10000 == 0:
                print(s)
        elif total <= 100000:
            if result_len % 20000 == 0:
                print(s)
        else:
            if result_len % 25000 == 0:
                print(s)

    return result


def get_follower_count(cred: TwitchCredentials, twitch_id: str, ) -> int:
    resp = twitch_api_get(
        twitch_url='https://api.twitch.tv/helix/users/follows',
        cred=cred,
        params={'to_id': twitch_id, 'first': 1},
    )
    return resp.json['total']


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
    """
    Gets the follower_relations recursively of a channel by twitch id
    This can be changed to use the twitch name as well instead of the id
    If the bearer_toke is not provided the limit for API Requests is 30 per minute
    If provided it is 800 per minute
    """

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
        print('found a total of ' + str(json['total']) + ' follower_relations for channel ' + str(twitch_id))
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


def get_channel_follows(twitch_id: str,
                        client_id: str,
                        page: str = None,
                        prev_result: {} = None,
                        sleep=6,
                        bearer_token=None,
                        print_state=False,
                        print_error=True,
                        print_headers=False) -> {}:
    """
    Gets the follows recursively of a user by twitch id
    This can be changed to use the twitch name as well instead of the id
    If the bearer_toke is not provided the limit for API Requests is 30 per minute
    If provided it is 800 per minute
    """
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
        print('found a total of ' + str(json['total']) + ' follower_relations for channel ' + str(twitch_id))
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


def __get_bearer_token(client_id: str, secret: str) -> {}:
    '''
    Get the bearer token
    '''
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
