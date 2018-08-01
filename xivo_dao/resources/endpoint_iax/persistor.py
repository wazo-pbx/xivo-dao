# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from functools import partial

from sqlalchemy import text

from xivo_dao.alchemy.useriax import UserIAX as IAX
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.helpers import errors, generators
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin

from .search import iax_search


class IAXPersistor(CriteriaBuilderMixin):

    _search_table = IAX

    def __init__(self, session, tenant_uuids=None):
        self.session = session
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        return self._find_query(criteria).first()

    def find_all_by(self, criteria):
        return self._find_query(criteria).all()

    def _find_query(self, criteria):
        query = self.session.query(IAX)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get(self, iax_id):
        iax = self.find_by({'id': iax_id})
        if not iax:
            raise errors.not_found('IAXEndpoint', id=iax_id)
        return iax

    def search(self, params):
        rows, total = iax_search.search(self.session, params)
        return SearchResult(total, rows)

    def create(self, iax):
        self.fill_default_values(iax)
        self.persist(iax)
        return self.get(iax.id)

    def persist(self, iax):
        self.session.add(iax)
        self.session.flush()
        self.session.expire(iax)

    def edit(self, iax):
        self.persist(iax)
        self._fix_associated(iax)

    def delete(self, iax):
        self.session.query(IAX).filter(IAX.id == iax.id).delete()
        self._fix_associated(iax)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(IAX.tenant_uuid.in_(self.tenant_uuids))

    def _fix_associated(self, iax):
        trunk_id = (self.session.query(Trunk.id)
                    .filter(Trunk.protocol == 'iax')
                    .filter(Trunk.protocolid == iax.id)
                    .scalar())
        if trunk_id:
            TrunkFixes(self.session).fix(trunk_id)

    def fill_default_values(self, iax):
        if iax.name is None:
            iax.name = generators.find_unused_hash(partial(self._already_exists, IAX.name))
        if iax.type is None:
            iax.type = 'friend'
        if iax.host is None:
            iax.host = 'dynamic'
        if iax.category is None:
            iax.category = 'trunk'

    def _already_exists(self, column, data):
        return self.session.query(IAX).filter(column == data).count() > 0
