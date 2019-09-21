# -*- coding: utf-8 -*-

class GithubAccount(object):
    tokens = ['']

    @classmethod
    def get_token(cls, seed):
        if seed < 0:
            seed = 0
        size = len(cls.tokens)
        return cls.tokens[seed % size]
