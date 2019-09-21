# -*- coding: utf-8 -*-
import time

import pandas as pd

from github.accounts.github_account import GithubAccount
from github.domain.github import GithubUser
from github.recorders.github.common import get_all_results
from zvdata.api import get_data, df_to_db
from zvdata.recorder import TimestampsDataRecorder
from zvdata.utils.time_utils import to_pd_timestamp, to_time_str, now_time_str, now_pd_timestamp


# use github search api to get all user list
class GithubUserListRecorder(TimestampsDataRecorder):
    # not useful,we're recording meta in fact
    entity_provider = 'github'
    entity_schema = GithubUser

    provider = 'github'
    data_schema = GithubUser
    # search between created dates [start_date,end_date]
    url = 'https://api.github.com/search/users?q=created%3A{}..{}'

    def __init__(self,
                 codes=None,
                 batch_size=50,
                 force_update=False,
                 sleeping_time=5,
                 default_size=2000,
                 one_shot=False,
                 fix_duplicate_way='ignore',
                 start_timestamp=None,
                 end_timestamp=None) -> None:
        super().__init__('github_user', ['github'], None, codes, batch_size, force_update, sleeping_time,
                         default_size, one_shot, fix_duplicate_way, start_timestamp, end_timestamp)

        self.seed = 0

    def init_entities(self):
        items = get_data(data_schema=self.data_schema, session=self.session, provider=self.provider,
                         entity_id='user_github_mojombo', filters=[self.data_schema.id == 'user_github_mojombo'],
                         return_type='domain')

        first_user = GithubUser(id='user_github_mojombo', entity_id='user_github_mojombo', node_id='MDQ6VXNlcjE=',
                                avatar_url='https://avatars0.githubusercontent.com/u/1?v=4',
                                gravatar_id=None, site_admin=False, code='mojombo', name='Tom Preston-Werner',
                                company=None, blog='http://tom.preston-werner.com', location='San Francisco',
                                email=None, hireable=False, bio=None, public_repos=61, public_gists=62, followers=21529,
                                following=11, timestamp=to_pd_timestamp(to_time_str("2007-10-20T05:24:19Z")),
                                created_timestamp=to_pd_timestamp(to_time_str("2007-10-20T05:24:19Z")),
                                updated_timestamp=to_pd_timestamp(to_time_str("2019-06-25T17:22:10Z")))

        if not items:
            self.session.add(first_user)
            self.session.commit()

        self.entities = [first_user]

    def init_timestamps(self, entity_item):
        # github start up from 2008
        start = max(to_pd_timestamp(entity_item.timestamp), to_pd_timestamp('2008-02-12'))
        return pd.date_range(start=start,
                             end=now_time_str(),
                             freq='1D').tolist()

    def get_latest_saved_record(self, entity):
        records = get_data(provider=self.provider,
                           data_schema=self.data_schema,
                           order=self.data_schema.timestamp.desc(), limit=1,
                           return_type='domain',
                           session=self.session)
        if records:
            return records[0]
        return None

    def record(self, entity_item, start, end, size, timestamps):
        self.seed += 1

        timestamp = timestamps[0]

        the_url = self.url.format(to_time_str(timestamp), to_time_str(timestamp))

        items = get_all_results(url=the_url, token=GithubAccount.get_token(seed=self.seed))

        current_time = now_pd_timestamp()

        results = [
            {
                'id': f'user_github_{item["login"]}',
                'entity_id': f'user_github_{item["login"]}',
                'timestamp': timestamp,
                'exchange': 'github',
                'entity_type': 'user',
                'code': item['login'],
                'node_id': item['node_id'],
                'created_timestamp': current_time,
                'updated_timestamp': None
            } for item in items]

        # for save faster
        df = pd.DataFrame(data=results[:-1])
        df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force=True)

        return results[-1:]

    def get_data_map(self):
        return {}

    def generate_domain_id(self, security_item, original_data):
        return original_data['id']


if __name__ == '__main__':
    while True:
        GithubUserListRecorder(batch_size=200).run()
        time.sleep(60)
