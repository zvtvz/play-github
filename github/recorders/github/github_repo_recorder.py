# -*- coding: utf-8 -*-
import argparse
import json

from github.accounts.github_account import GithubAccount
from github.domain.github import GithubUser, GithubRepo
from github.recorders.github.common import get_result
from zvdata.api import get_entities
from zvdata.domain import get_db_session
from zvdata.recorder import TimeSeriesDataRecorder
from zvdata.utils.time_utils import now_pd_timestamp, TIME_FORMAT_DAY, to_pd_timestamp


class GithubRepoRecorder(TimeSeriesDataRecorder):
    entity_provider = 'github'
    entity_schema = GithubUser

    provider = 'github'
    data_schema = GithubRepo

    url = 'https://api.github.com/users/{}/repos'
    repo_url = 'https://api.github.com/repos/{}/{}'
    topics_url = 'https://api.github.com/repos/{}/{}/topics'

    def __init__(self, codes=None, batch_size=50,
                 force_update=True, sleeping_time=5, default_size=2000, real_time=False, fix_duplicate_way='ignore',
                 start_timestamp=None, end_timestamp=None) -> None:
        super().__init__('github_user', ['github'], None, codes, batch_size, force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, start_timestamp, end_timestamp)
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
                                     start_timestamp=self.start_timestamp,
                                     end_timestamp=self.end_timestamp)

    def record(self, entity_item, start, end, size, timestamps):
        self.seed += 1

        the_url = self.url.format(entity_item.code)
        repo_infos = get_result(url=the_url, token=GithubAccount.get_token(seed=self.seed))
        for repo_info in repo_infos:
            # get topics
            topics_url = self.topics_url.format(entity_item.code, repo_info['name'])
            topics = get_result(url=topics_url, token=GithubAccount.get_token(seed=self.seed),
                                headers={'Accept': 'application/vnd.github.mercy-preview+json'})

            if topics:
                repo_info['topics'] = topics['names']

            repo_info['updated_timestamp'] = now_pd_timestamp()
            repo_info['code'] = entity_item.code
            repo_info['timestamp'] = to_pd_timestamp(repo_info['created_at'])
        return repo_infos

    def get_data_map(self):
        return {
            'node_id': 'node_id',
            'name': 'name',
            'full_name': 'full_name',
            'private': 'private',
            'language': ('language', json.dumps),
            'forks_count': 'forks_count',
            'stargazers_count': 'stargazers_count',
            'watchers_count': 'watchers_count',
            'size': 'size',
            'open_issues_count': 'open_issues_count',
            'topics': ('topics', json.dumps),
            'pushed_at': ('pushed_at', to_pd_timestamp),
            'created_at': ('created_at', to_pd_timestamp),
            'updated_at': ('updated_at', to_pd_timestamp),
            'subscribers_count': 'subscribers_count',
            'network_count': 'network_count',
            'license': ('license', json.dumps),
            'updated_timestamp': 'updated_timestamp',
            'timestamp': ('created_at', to_pd_timestamp)
        }

    def generate_domain_id(self, entity, original_data, time_fmt=TIME_FORMAT_DAY):
        return "{}_{}".format(entity.id, original_data['name'])

    def evaluate_start_end_size_timestamps(self, entity):
        latest_record = self.get_latest_saved_record(entity=entity)

        if latest_record:
            latest_timestamp = latest_record.updated_timestamp
            if latest_timestamp is not None:
                if (now_pd_timestamp() - latest_timestamp).days < 10:
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

    recorder = GithubRepoRecorder(start_timestamp=start, end_timestamp=end)

    recorder.run()
