# -*- coding: utf-8 -*-
from typing import List

import requests

from github.accounts.github_account import GithubAccount


def request_with_auth(url, method='get', data=None, token=None, headers=None):
    if token is None:
        token = GithubAccount.get_token(0)

    if headers:
        headers['Authorization'] = f'token {token}'
    else:
        headers = {
            'Authorization': f'token {token}'
        }

    if method == 'get':
        response = requests.get(url=url, headers=headers)
    elif method == 'put':
        response = requests.put(url=url, data=data, headers=headers)
    else:
        response = requests.post(url=url, data=data, headers=headers)

    return response


def get_result(url, token=None, headers=None):
    response = request_with_auth(url=url, token=token, headers=headers)

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise Exception(f'request {url} error_code:{response.status_code},msg:{response.text}')

    return response.json()


def get_all_results(url, per_page=50, token=None):
    url = f'{url}&per_page={per_page}'
    response = request_with_auth(url=url, token=token)

    if response.status_code != 200:
        raise Exception(f'request {url} error_code:{response.status_code},msg:{response.text}')

    items: List = response.json()['items']

    link: str = response.headers.get('Link')
    if link:
        # Link: <https://api.github.com/resource?page=2>; rel="next",
        #       <https://api.github.com/resource?page=5>; rel="last"
        page_count = int(link.split(',')[-1].split(';')[0].replace('<', '').replace('>', '').split('page=')[-1])

        if page_count >= 2:
            for page in range(2, page_count + 1):
                response = request_with_auth(url=f'{url}&page={page}', token=token)

                if response.status_code != 200:
                    raise Exception(f'request {url} error_code:{response.status_code},msg:{response.text}')

                items += response.json()['items']

    return items
