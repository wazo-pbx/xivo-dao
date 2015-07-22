# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
import re


class Line(AbstractModels):

    MANDATORY = [
        'context',
        'protocol',
        'device_slot'
    ]

    # mapping = {db_field: model_field}
    _MAPPING = {
        'id': 'id',
        'name': 'name',
        'number': 'number',
        'context': 'context',
        'protocol': 'protocol',
        'protocolid': 'protocolid',
        'callerid': 'callerid',
        'device': 'device_id',
        'provisioningid': 'provisioning_extension',
        'configregistrar': 'configregistrar',
        'num': 'device_slot'
    }

    _RELATION = {}

    def __init__(self, *args, **kwargs):
        AbstractModels.__init__(self, *args, **kwargs)

    def _clean_device_id(self):
        if hasattr(self, 'device_id') and self.device_id == '':
            self.device_id = None

    @classmethod
    def from_data_source(cls, db_object):
        model = super(Line, cls).from_data_source(db_object)
        model.provisioning_extension = str(model.provisioning_extension)
        model._clean_device_id()
        return model

    def update_from_data_source(self, db_object):
        AbstractModels.update_from_data_source(self, db_object)
        self.provisioning_extension = str(self.provisioning_extension)
        self._clean_device_id()

    def to_data_source(self, class_schema):
        source = AbstractModels.to_data_source(self, class_schema)
        if hasattr(source, 'provisioningid'):
            source.provisioningid = int(source.provisioningid)
        if hasattr(source, 'device') and source.device is None:
            source.device = ''
        return source

    @property
    def interface(self):
        return '%s/%s' % (self.protocol.upper(), self.name)


class LineOrdering(object):
        name = LineSchema.name
        context = LineSchema.context


class LineSIP(Line):

    # mapping = {db_field: model_field}
    _MAPPING = dict(Line._MAPPING.items() + {
        'username': 'username',
        'secret': 'secret',
    }.items())

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'sip'

    @classmethod
    def from_data_source(cls, db_object):
        obj = super(LineSIP, cls).from_data_source(db_object)
        if hasattr(obj, 'name'):
            obj.username = db_object.name

        return obj

    def to_data_source(self, class_schema):
        obj = super(LineSIP, self).to_data_source(class_schema)
        if hasattr(self, 'username'):
            obj.name = self.username
        del obj.username
        return obj

    def to_data_dict(self):
        data_dict = super(LineSIP, self).to_data_dict()
        if hasattr(self, 'username'):
            data_dict['name'] = self.username
        del data_dict['username']
        return data_dict

    def update_from_data(self, data_dict):
        super(LineSIP, self).update_from_data(data_dict)
        if 'name' in data_dict:
            self.username = data_dict['name']

    def update_from_data_source(self, db_object):
        super(LineSIP, self).update_from_data_source(db_object)
        if hasattr(db_object, 'name'):
            self.username = db_object.name

    def update_data_source(self, db_object):
        super(LineSIP, self).update_data_source(db_object)
        if hasattr(self, 'username'):
            setattr(db_object, 'name', self.username)
        setattr(db_object, 'username', '')
        if hasattr(db_object, 'device') and db_object.device is None:
            db_object.device = ''

    def extract_displayname(self):
        return re.match(r'^"(.+)"', self.callerid).group(1)


class LineIAX(Line):

    # mapping = {db_field: model_field}
    _MAPPING = dict(Line._MAPPING.items() + {
        'username': 'username',
        'secret': 'secret'
    }.items())

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'iax'


class LineSCCP(Line):

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'sccp'


class LineCUSTOM(Line):

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        self.protocol = 'custom'
