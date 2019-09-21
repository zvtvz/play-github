# -*- coding: utf-8 -*-
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from github.accounts.github_account import GithubAccount
from github.domain import GithubRepo
from github.recorders.github.common import request_with_auth
from zvdata.api import get_data
from zvdata.utils.utils import init_process_log

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()

url = 'https://api.github.com/user/starred/{}/{}'


@sched.scheduled_job('interval', hours=1)
def star_some_repo():
    import random
    year = random.randint(2012, 2014)
    mon = random.randint(1, 12)
    day = random.randint(1, 28)

    start_timestamp = f'{year}-{mon}-{day}'

    year = random.randint(2015, 2019)
    mon = random.randint(1, 12)
    day = random.randint(1, 28)

    end_timestamp = f'{year}-{mon}-{day}'

    repos = get_data(provider='github', data_schema=GithubRepo, start_timestamp=start_timestamp,
                     end_timestamp=end_timestamp, return_type='domain', limit=5000)

    for seed in range(0, len(GithubAccount.tokens)):
        for repo in repos:
            resp = request_with_auth(url=url.format(repo.code, repo.name), method='put',
                                     token=GithubAccount.get_token(seed=seed),
                                     headers={'Content-Length': '0'})
            if resp.status_code == 204:
                print('star:{} ok'.format(repo.full_name))
            else:
                print(resp.status_code)


if __name__ == '__main__':
    init_process_log('star_some_repo.log')

    star_some_repo()

    sched.start()

    sched._thread.join()
