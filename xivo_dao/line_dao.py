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

from sqlalchemy import and_

from xivo.asterisk.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension as ExtensionTable
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.enum import valid_trunk_protocols


@daosession
def get_interface_from_exten_and_context(session, extension, context):
    res = (session
           .query(LineFeatures.protocol,
                  LineFeatures.name,
                  UserLine.main_line)
           .join(LineExtension, LineExtension.line_id == LineFeatures.id)
           .join(ExtensionTable, LineExtension.extension_id == ExtensionTable.id)
           .outerjoin(UserLine, UserLine.line_id == LineFeatures.id)
           .filter(ExtensionTable.exten == extension)
           .filter(ExtensionTable.context == context))

    interface = None
    for row in res.all():
        interface = _format_interface(row.protocol, row.name)
        if row.main_line:
            return interface

    if not interface:
        raise LookupError('no line with extension %s and context %s' % (extension, context))

    return interface


@daosession
def get_extension_from_protocol_interface(session, protocol, interface):
    lowered_protocol = protocol.lower()
    if lowered_protocol not in valid_trunk_protocols:
        raise ValueError('{} is not a valid line protocol'.format(protocol))

    row = (session
           .query(ExtensionTable.exten, ExtensionTable.context)
           .join(LineExtension,
                 and_(LineExtension.extension_id == ExtensionTable.id,
                      LineExtension.main_extension == True))  # noqa
           .join(LineFeatures, LineExtension.line_id == LineFeatures.id)
           .filter(LineFeatures.protocol == lowered_protocol)
           .filter(LineFeatures.name == interface)
           .first())

    if not row:
        message = 'no line with interface %s' % interface
        raise LookupError(message)

    extension = Extension(number=row.exten, context=row.context, is_internal=True)
    return extension


@daosession
def get_peer_name(session, device_id):
    row = (session
           .query(LineFeatures.name, LineFeatures.protocol)
           .filter(LineFeatures.device == str(device_id))).first()

    if not row:
        raise LookupError('No such device')

    return '/'.join([row.protocol, row.name])


@daosession
def get_protocol(session, line_id):
    row = session.query(LineFeatures).filter(LineFeatures.id == line_id).first()
    if not row:
        raise LookupError
    return row.protocol


def _format_interface(protocol, name):
    if protocol == 'custom':
        return name
    else:
        return '%s/%s' % (protocol.upper(), name)


@daosession
def get(session, lineid):
    return session.query(LineFeatures).filter(LineFeatures.id == lineid).first()
