# -*- coding: utf-8 -*-
import argparse

from github.accounts.github_account import GithubAccount
from github.domain.github import GithubUser
from github.recorders.github.common import get_result
from zvdata.api import get_entities
from zvdata.domain import get_db_session
from zvdata.recorder import TimeSeriesDataRecorder
from zvdata.utils.time_utils import day_offset_today, now_pd_timestamp


class GithubUserInfoRecorder(TimeSeriesDataRecorder):
    entity_provider = 'github'
    entity_schema = GithubUser

    provider = 'github'
    data_schema = GithubUser

    url = 'https://api.github.com/users/{}'

    def __init__(self,
                 codes=None,
                 batch_size=50,
                 force_update=True,
                 sleeping_time=5,
                 default_size=2000,
                 one_shot=True,
                 fix_duplicate_way='ignore',
                 start_timestamp=None,
                 end_timestamp=None) -> None:
        super().__init__('github_user', ['github'], None, codes, batch_size, force_update, sleeping_time,
                         default_size, one_shot, fix_duplicate_way, start_timestamp, end_timestamp)

        self.seed = 0

    def init_entities(self):
        if self.entity_provider == self.provider and self.entity_schema == self.data_schema:
            self.entity_session = self.session
        else:
            self.entity_session = get_db_session(provider=self.entity_provider, data_schema=self.entity_schema)

        # init the entity list
        self.entities = get_entities(session=self.entity_session,
                                     entity_type=self.entity_type,
                                     entity_ids=self.entity_ids,
                                     codes=self.codes,
                                     return_type='domain',
                                     provider=self.entity_provider,
                                     # 最近７天更新过的跳过
                                     filters=[(GithubUser.updated_timestamp < day_offset_today(
                                         -7)) | (GithubUser.updated_timestamp.is_(None))],
                                     start_timestamp=self.start_timestamp,
                                     end_timestamp=self.end_timestamp)

    def record(self, entity_item, start, end, size, timestamps):
        self.seed += 1

        the_url = self.url.format(entity_item.code)
        user_info = get_result(url=the_url, token=GithubAccount.get_token(seed=self.seed))
        if user_info:
            user_info['updated_timestamp'] = now_pd_timestamp()
            return [user_info]
        return []

    def get_data_map(self):
        return {
            'site_admin': 'site_admin',
            'name': 'name',
            'avatar_url': 'avatar_url',
            'gravatar_id': 'gravatar_id',
            'company': 'company',
            'blog': 'blog',
            'location': 'location',
            'email': 'email',
            'hireable': 'hireable',
            'bio': 'bio',
            'public_repos': 'public_repos',
            'public_gists': 'public_gists',
            'followers': 'followers',
            'following': 'following',
            'updated_timestamp': 'updated_timestamp'
        }

    def generate_domain_id(self, security_item, original_data):
        return security_item.id

    def evaluate_start_end_size_timestamps(self, entity):
        latest_record = self.get_latest_saved_record(entity=entity)

        if latest_record:
            latest_timestamp = latest_record.updated_timestamp
            if latest_timestamp is not None:
                if (now_pd_timestamp() - latest_timestamp).days < 7:
                    self.logger.info('entity_item:{},updated_timestamp:{},ignored'.format(entity.id, latest_timestamp))
                    return None, None, 0, None

        return None, None, self.default_size, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', help='start_timestamp', default='2015-01-01')
    parser.add_argument('--end', help='end_timestamp', default='2015-12-31')

    args = parser.parse_args()
    start = args.start
    end = args.end

    recorder = GithubUserInfoRecorder(start_timestamp=start, end_timestamp=end)

    recorder.run()
