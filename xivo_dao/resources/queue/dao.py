# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def exists(session, queue_id):
    query = (session.query(QueueFeatures)
             .filter(QueueFeatures.id == queue_id)
             )

    return query.count() > 0


@daosession
def find_by(session, name):
    query = (session.query(QueueFeatures)
             .filter_by(name=name)
             )

    return query.first()
