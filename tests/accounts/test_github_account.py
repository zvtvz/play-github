# -*- coding: utf-8 -*-
from github.accounts.github_account import GithubAccount


def test_get_token():
    current_token = GithubAccount.get_token(0)
    for i in range(1, 100):
        new_token = GithubAccount.get_token(i)
        assert new_token != None
        assert new_token != current_token
        current_token = new_token
