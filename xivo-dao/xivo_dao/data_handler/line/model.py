# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.helpers.abstract_model import AbstractModels


class Line(AbstractModels):

    MANDATORY = [
        'name',
        'context',
        'protocol'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'name': 'name',
        # 'number': 'number',
        'context': 'context',
        'protocol': 'protocol',
        'callerid': 'callerid',
        'deviceid': 'deviceid',
        'num': 'num'
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)

    @property
    def interface(self):
        return '%s/%s' % (self.protocol.upper(), self.name)


class LineSIP(Line):

    MANDATORY = [
        'username',
        'secret'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'username': 'username',
        'secret': 'secret'
    }

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
