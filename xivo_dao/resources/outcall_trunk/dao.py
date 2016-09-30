# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.outcall_trunk.persistor import Persistor


def persistor():
    return Persistor(Session)


def get_by(**criteria):
    return persistor().get_by(**criteria)


def find_by(**criteria):
    return persistor().find_by(**criteria)


def find_all_by(**criteria):
    return persistor().find_all_by(**criteria)


def associate_all_trunks(outcall, trunks):
    return persistor().associate_all_trunks(outcall, trunks)


def dissociate_all_by_outcall(outcall):
    return persistor().dissociate_all_trunks_by_outcall(outcall)
