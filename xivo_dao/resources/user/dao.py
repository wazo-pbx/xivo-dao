# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from sqlalchemy import and_

from xivo_dao.helpers.db_manager import Session

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from xivo_dao.resources.user.persistor import UserPersistor
from xivo_dao.resources.func_key.persistor import DestinationPersistor
from xivo_dao.resources.func_key_template.persistor import build_persistor as build_template_persistor
from xivo_dao.resources.user.search import user_search
from xivo_dao.resources.user.view import user_view
from xivo_dao.resources.user.fixes import UserFixes


def persistor(tenant_uuids=None):
    return UserPersistor(Session, user_view, user_search, tenant_uuids)


def legacy_search(term, tenant_uuids):
    users = (Session.query(User)
             .filter(and_(User.fullname.ilike('%{}%'.format(term)),
                          User.tenant_uuid.in_(tenant_uuids)))
             .all()
             )

    return SearchResult(len(users), users)


def search(**parameters):
    tenant_uuids = parameters.pop('tenant_uuids', None)
    return persistor(tenant_uuids).search(parameters)


def get(user_id):
    return persistor().get_by({'id': user_id})


def get_by(**criteria):
    return persistor().get_by(criteria)


def find_by_id_uuid(id):
    return persistor().find_by_id_uuid(id)


def get_by_id_uuid(id):
    return persistor().get_by_id_uuid(id)


def find_all_by_agent_id(agent_id):
    return persistor().find_all_by_agent_id(agent_id)


def find(user_id):
    return persistor().find_by({'id': user_id})


def find_by(**criteria):
    return persistor().find_by(criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(criteria)


def create(user):
    created_user = persistor().create(user)
    DestinationPersistor(Session).create_user_destination(created_user)
    return created_user


def edit(user):
    persistor().edit(user)
    UserFixes(Session).fix(user.id)


def delete(user):
    DestinationPersistor(Session).delete_user_destination(user)
    persistor().delete(user)
    template_persistor = build_template_persistor(Session)
    template_persistor.delete(user.func_key_template_private)


def associate_all_groups(user, groups):
    persistor().associate_all_groups(user, groups)
