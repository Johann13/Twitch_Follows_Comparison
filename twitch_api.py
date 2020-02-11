import time

import requests

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
def get_bearer_token(client_id: str, secret: str) -> {}:
    twitch_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post(twitch_url, params=params)
    return response.json()


'''
Returns a tuple of client id and token.
'''
def get_cred(client_id: str, secret: str) -> (str, str):
    token = get_bearer_token(client_id, secret)['access_token']
    return client_id, token
