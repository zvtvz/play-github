# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from github.accounts.github_account import GithubAccount
from github.domain import GithubUser
from github.recorders.github.common import request_with_auth
from zvdata.api import get_data
from zvdata.utils.utils import init_process_log

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()

url = 'https://api.github.com/user/following/{}'


@sched.scheduled_job('interval', hours=1)
def follow_someone():
    import random
    year = random.randint(2012, 2014)
    mon = random.randint(1, 12)
    day = random.randint(1, 28)

    start_timestamp = f'{year}-{mon}-{day}'

    year = random.randint(2015, 2019)
    mon = random.randint(1, 12)
    day = random.randint(1, 28)

    end_timestamp = f'{year}-{mon}-{day}'

    users = get_data(provider='github', data_schema=GithubUser, start_timestamp=start_timestamp,
                     end_timestamp=end_timestamp, return_type='domain', limit=1000)

    for seed in range(0, len(GithubAccount.tokens)):
        for user in users:
            resp = request_with_auth(url=url.format(user.code), method='put',
                                     token=GithubAccount.get_token(seed=seed),
                                     headers={'Content-Length': '0'})
            if resp.status_code == 204:
                print('follow:{} ok'.format(user.code))
            else:
                print(resp.status_code)


if __name__ == '__main__':
    init_process_log('follow_someone.log')

    follow_someone()

    sched.start()

    sched._thread.join()
