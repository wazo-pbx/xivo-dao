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

import unittest
import logging

from mock import patch
from xivo_dao.helpers.db_manager import Base
from sqlalchemy.schema import MetaData
from xivo_dao.helpers import config
from xivo_dao.helpers import db_manager
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.extenumber import ExteNumber
from xivo_dao.alchemy.devicefeatures import DeviceFeatures

logger = logging.getLogger(__name__)


class DAOTestCase(unittest.TestCase):

    @classmethod
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def setUpClass(cls, send_bus_command):
        logger.debug("Connecting to database")
        config.DB_URI = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        config.XIVO_DB_URI = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        db_manager._init()
        cls.session = db_manager.AsteriskSession()
        cls.engine = cls.session.bind
        logger.debug("Connected to database")
        cls.cleanTables()

    @classmethod
    def tearDownClass(cls):
        logger.debug("Closing connection")
        cls.session.close()

    @classmethod
    def cleanTables(cls):
        logger.debug("Cleaning tables")
        cls.session.begin()

        if cls.tables:
            engine = cls.engine

            meta = MetaData(engine)
            meta.reflect()
            logger.debug("drop all tables")
            meta.drop_all()

            table_list = [table.__table__ for table in cls.tables]
            logger.debug("create all tables")
            Base.metadata.create_all(engine, table_list)
            engine.dispose()

        cls.session.commit()
        logger.debug("Tables cleaned")

    def empty_tables(self):
        logger.debug("Emptying tables")
        table_names = [table.__tablename__ for table in self.tables]
        self.session.begin()
        self.session.execute("TRUNCATE %s CASCADE;" % ",".join(table_names))
        self.session.commit()
        logger.debug("Tables emptied")

    def add_me(self, obj):
        self.session.begin()
        try:
            self.session.add(obj)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def add_line(self, **kwargs):
        kwargs.setdefault('name', 'fooname')
        kwargs.setdefault('context', 'foocontext')
        kwargs.setdefault('protocolid', 1)
        kwargs.setdefault('provisioningid', 1)

        line = LineFeatures(**kwargs)
        self.add_me(line)
        return line.id

    def add_user_line(self, **kwargs):
        kwargs.setdefault('main_user', True)

        user_line = UserLine(**kwargs)
        self.add_me(user_line)

    def add_extenumber(self, **kwargs):
        kwargs.setdefault('type', 'user')

        extenumber = ExteNumber(**kwargs)
        self.add_me(extenumber)
        return extenumber.id

    def add_user(self, **kwargs):
        user = UserFeatures(**kwargs)
        self.add_me(user)
        return user.id

    def add_device(self, **kwargs):
        kwargs.setdefault('deviceid', '8aada8aae3784957b6c160195c8fbcd7')
        kwargs.setdefault('mac', '00:08:5d:13:ca:05')
        kwargs.setdefault('vendor', 'Aastra')
        kwargs.setdefault('model', '6739i')
        kwargs.setdefault('plugin', 'xivo-aastra-3.2.2.1136')
        kwargs.setdefault('proto', 'SIP')

        device = DeviceFeatures(**kwargs)
        self.add_me(device)
        return device.id

    def add_me_all(self, obj_list):
        self.session.begin()
        self.session.add_all(obj_list)
        self.session.commit()
