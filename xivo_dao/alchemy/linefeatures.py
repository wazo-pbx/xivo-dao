# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from __future__ import unicode_literals

import re
import six

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import cast, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Text
from sqlalchemy.schema import Column, UniqueConstraint, PrimaryKeyConstraint, Index
from sqlalchemy.ext.hybrid import hybrid_property

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy import enum


caller_id_regex = re.compile(r'''
                             "                      #name start
                             (?P<name>[^"]+)        #inside ""
                             "                      #name end
                             \s+                    #space between name and number
                             (
                             <                      #number start
                             (?P<num>\+?[\dA-Z]+)   #inside <>
                             >                      #number end
                             )?                     #number is optional
                             ''', re.VERBOSE)


class LineFeatures(Base):

    CALLER_ID = '"{name}" <{num}>'

    __tablename__ = 'linefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        UniqueConstraint('protocol', 'protocolid'),
        Index('linefeatures__idx__context', 'context'),
        Index('linefeatures__idx__device', 'device'),
        Index('linefeatures__idx__number', 'number'),
        Index('linefeatures__idx__provisioningid', 'provisioningid'),
    )

    id = Column(Integer)
    protocol = Column(enum.trunk_protocol)
    protocolid = Column(Integer)
    device = Column(String(32))
    configregistrar = Column(String(128))
    name = Column(String(128))
    number = Column(String(40))
    context = Column(String(39), nullable=False)
    provisioningid = Column(Integer, nullable=False)
    num = Column(Integer, server_default='1')
    ipfrom = Column(String(15))
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    endpoint_sip = relationship('UserSIP',
                                primaryjoin="""and_(
                                    LineFeatures.protocol == 'sip',
                                    LineFeatures.protocolid == UserSIP.id
                                )""",
                                foreign_keys='LineFeatures.protocolid',
                                back_populates='line')

    endpoint_sccp = relationship('SCCPLine',
                                 primaryjoin="""and_(
                                     LineFeatures.protocol == 'sccp',
                                     LineFeatures.protocolid == SCCPLine.id
                                 )""",
                                 foreign_keys='LineFeatures.protocolid',
                                 back_populates='line')

    endpoint_custom = relationship('UserCustom',
                                   primaryjoin="""and_(
                                       LineFeatures.protocol == 'custom',
                                       LineFeatures.protocolid == UserCustom.id
                                   )""",
                                   foreign_keys='LineFeatures.protocolid',
                                   back_populates='line')

    line_extensions = relationship('LineExtension',
                                   order_by='desc(LineExtension.main_extension)',
                                   cascade='all, delete-orphan',
                                   back_populates='line')

    extensions = association_proxy('line_extensions', 'extension')

    user_lines = relationship('UserLine',
                              order_by='desc(UserLine.main_user)',
                              cascade='all, delete-orphan',
                              back_populates='line')

    users = association_proxy('user_lines', 'user')

    @property
    def caller_id_name(self):
        if self.protocol == 'sip':
            return self._sip_caller_id_name()
        elif self.protocol == 'sccp':
            return self._sccp_caller_id_name()

    def _sip_caller_id_name(self):
        if self.endpoint_sip is None:
            return None

        if self.endpoint_sip.callerid is None:
            return None

        match = caller_id_regex.match(self.endpoint_sip.callerid)
        if not match:
            return None

        return match.group('name')

    def _sccp_caller_id_name(self):
        if self.endpoint_sccp is None:
            return None

        return self.endpoint_sccp.cid_name

    @caller_id_name.setter
    def caller_id_name(self, value):
        if value is None:
            if self.protocol is not None:
                raise InputError("Cannot set caller id to None")
        else:
            if self.protocol == 'sip':
                self._set_sip_caller_id_name(value)
            elif self.protocol == 'sccp':
                self._set_sccp_caller_id_name(value)
            elif self.protocol == 'custom':
                raise InputError("Cannot set caller id on endpoint of type 'custom'")
            else:
                raise InputError("Unsupported caller id protocol")

    def _set_sip_caller_id_name(self, value):
        num = self._sip_caller_id_num()
        callerid = self.CALLER_ID.format(name=value, num=num)
        self.endpoint_sip.callerid = callerid

    def _set_sccp_caller_id_name(self, value):
        self.endpoint_sccp.cid_name = value

    @property
    def caller_id_num(self):
        if self.protocol == 'sip':
            return self._sip_caller_id_num()
        elif self.protocol == 'sccp':
            return self._sccp_caller_id_num()

    def _sip_caller_id_num(self):
        if self.endpoint_sip is None:
            return None

        if self.endpoint_sip.callerid is None:
            return None

        match = caller_id_regex.match(self.endpoint_sip.callerid)
        if not match:
            return None

        return match.group('num')

    def _sccp_caller_id_num(self):
        if self.endpoint_sccp is None:
            return None

        return self.endpoint_sccp.cid_num

    @caller_id_num.setter
    def caller_id_num(self, value):
        if value is None:
            if self.protocol is not None:
                raise InputError("Cannot set caller id num to None")
        else:
            if self.protocol == 'sip':
                self._set_sip_caller_id_num(value)
            elif self.protocol == 'sccp':
                raise InputError("Cannot set caller id num on endpoint of type 'sccp'")
            elif self.protocol == 'custom':
                raise InputError("Cannot set caller id on endpoint of type 'custom'")
            else:
                raise InputError("Unsupported caller id protocol")

    def _set_sip_caller_id_num(self, value):
        name = self._sip_caller_id_name()
        callerid = self.CALLER_ID.format(name=name, num=value)
        self.endpoint_sip.callerid = callerid

    @hybrid_property
    def endpoint(self):
        return self.protocol

    @endpoint.setter
    def endpoint(self, value):
        self.protocol = value

    @hybrid_property
    def endpoint_id(self):
        return self.protocolid

    @endpoint_id.setter
    def endpoint_id(self, value):
        self.protocolid = value

    @hybrid_property
    def provisioning_extension(self):
        return self.provisioning_code

    @hybrid_property
    def provisioning_code(self):
        if self.provisioningid is None:
            return None
        return six.text_type(self.provisioningid)

    @provisioning_code.expression
    def provisioning_code(cls):
        return cast(func.nullif(cls.provisioningid, 0), String)

    @provisioning_code.setter
    def provisioning_code(self, value):
        if value is None:
            self.provisioningid = None
        elif value.isdigit():
            self.provisioningid = int(value)

    @hybrid_property
    def position(self):
        return self.num

    @position.setter
    def position(self, value):
        self.num = value

    @hybrid_property
    def device_slot(self):
        return self.num

    @hybrid_property
    def device_id(self):
        if self.device == '':
            return None
        return self.device

    @device_id.expression
    def device_id(cls):
        return func.nullif(cls.device, '')

    @device_id.setter
    def device_id(self, value):
        value = value or ''
        self.device = value

    @hybrid_property
    def registrar(self):
        return self.configregistrar

    @registrar.setter
    def registrar(self, value):
        self.configregistrar = value

    def is_associated(self, protocol=None):
        if protocol:
            return self.protocol == protocol and self.protocolid is not None
        return self.protocol is not None and self.protocolid is not None

    def is_associated_with(self, endpoint):
        return endpoint.same_protocol(self.protocol, self.protocolid)

    def associate_endpoint(self, endpoint):
        self.protocol = endpoint.endpoint_protocol()
        self.protocolid = endpoint.id

    def remove_endpoint(self):
        self.protocol = None
        self.protocolid = None

    def update_extension(self, extension):
        self.number = extension.exten
        self.context = extension.context

    def clear_extension(self):
        self.number = None

    def update_name(self):
        if self.endpoint_sip and self.endpoint_sip.name not in ("", None):
            self.name = self.endpoint_sip.name
        elif self.endpoint_sccp and self.endpoint_sccp.name not in ("", None):
            self.name = self.endpoint_sccp.name
        elif self.endpoint_custom and self.endpoint_custom.interface not in ("", None):
            self.name = self.endpoint_custom.interface
        else:
            self.name = None

    def associate_device(self, device):
        self.device = device.id

    def remove_device(self):
        self.device = ''
