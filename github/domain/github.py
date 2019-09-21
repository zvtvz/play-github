# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

from zvdata import NormalEntityMixin, NormalMixin
from zvdata.domain import register_entity, register_schema

GithubUserBase = declarative_base()
GithubRepoBase = declarative_base()


@register_entity(entity_type='github_user')
class GithubUser(GithubUserBase, NormalEntityMixin):
    __tablename__ = 'github_user'

    node_id = Column(String(length=128))
    avatar_url = Column(String(length=256))
    gravatar_id = Column(String(length=128))
    site_admin = Column(Boolean)

    # the name of the person
    name = Column(String(length=128))
    company = Column(String(length=128))
    blog = Column(String(length=128))
    location = Column(String(length=128))
    email = Column(String(length=128))
    hireable = Column(String(length=128))
    bio = Column(String(length=256))
    public_repos = Column(Integer)
    public_gists = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)


class GithubRepo(GithubRepoBase, NormalMixin):
    __tablename__ = 'github_repo'

    code = Column(String(length=64))
    node_id = Column(String(length=128))
    name = Column(String(length=128))
    full_name = Column(String(length=128))

    private = Column(Boolean)
    language = Column(String(length=512))
    forks_count = Column(Integer)
    stargazers_count = Column(Integer)
    watchers_count = Column(Integer)
    size = Column(Integer)
    open_issues_count = Column(Integer)
    topics = Column(String(length=512))
    pushed_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    subscribers_count = Column(Integer)
    network_count = Column(Integer)
    license = Column(String(512))


register_schema(providers=['github'], db_name='github_user', schema_base=GithubUserBase, entity_type='github_user')

register_schema(providers=['github'], db_name='github_repo', schema_base=GithubRepoBase, entity_type='github_user')
