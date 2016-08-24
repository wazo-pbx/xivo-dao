# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_dao.resources.utils.search import CriteriaBuilderMixin
from xivo_dao.resources.extension.fixes import ExtensionFixes
from xivo_dao.resources.line.fixes import LineFixes

from xivo_dao.helpers import errors
from xivo_dao.alchemy.line_extension import LineExtension


class LineExtensionPersistor(CriteriaBuilderMixin):

    _search_table = LineExtension

    def __init__(self, session):
        self.session = session

    def find_query(self, **criteria):
        query = self.session.query(LineExtension)
        return self.build_criteria(query, criteria)

    def find_by(self, **criteria):
        return self.find_query(**criteria).first()

    def get_by(self, **criteria):
        line_extension = self.find_by(**criteria)
        if not line_extension:
            raise errors.not_found('LineExtension', **criteria)
        return line_extension

    def find_all_by(self, **criteria):
        return self.find_query(**criteria).all()

    def associate_line_extension(self, line, extension):
        line_main_extension = self.find_by(main_extension=True, line_id=line.id)

        line_extension = LineExtension(line_id=line.id,
                                       extension_id=extension.id,
                                       main_extension=(False if line_main_extension else True))

        self.session.add(line_extension)
        self.session.flush()
        ExtensionFixes(self.session).fix_extension(line_extension.extension_id)
        LineFixes(self.session).fix(line_extension.line_id)

        return line_extension

    def dissociate_line_extension(self, line, extension):
        line_extension = self.get_by(line_id=line.id, extension_id=extension.id)

        if line_extension.main_extension:
            self._set_oldest_main_extension(line)

        self.session.delete(line_extension)
        self.session.flush()
        ExtensionFixes(self.session).fix_extension(line_extension.extension_id)
        LineFixes(self.session).fix(line_extension.line_id)

        return line_extension

    def _set_oldest_main_extension(self, line):
        oldest_line_extension = (self.session.query(LineExtension)
                                 .filter(LineExtension.line_id == line.id)
                                 .filter(LineExtension.main_extension == False)  # noqa
                                 .order_by(LineExtension.extension_id.asc())
                                 .first())

        if oldest_line_extension:
            oldest_line_extension.main_extension = True
            self.session.add(oldest_line_extension)