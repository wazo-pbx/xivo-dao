# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from xivo_dao import trunk_dao
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.tests.test_dao import DAOTestCase


class TrunkFeaturesDAOTestCase(DAOTestCase):

    def test_find_by_proto_name_sip(self):
        trunk_name = 'my_trunk'

        trunk = TrunkFeatures()
        trunk.protocolid = 5436
        trunk.protocol = 'sip'

        usersip = UserSIP()
        usersip.id = trunk.protocolid
        usersip.name = trunk_name
        usersip.type = 'peer'
        usersip.category = 'user'

        self.add_me_all([trunk, usersip])

        result = trunk_dao.find_by_proto_name('sip', trunk_name)

        self.assertEqual(result, trunk.id)

    def test_find_by_proto_name_iax(self):
        trunk_name = 'my_trunk'

        trunk = TrunkFeatures()
        trunk.protocolid = 5454
        trunk.protocol = 'iax'

        useriax = UserIAX()
        useriax.id = trunk.protocolid
        useriax.name = trunk_name
        useriax.type = 'peer'
        useriax.category = 'user'

        self.add_me_all([trunk, useriax])

        result = trunk_dao.find_by_proto_name('iax', trunk_name)

        self.assertEqual(result, trunk.id)

    def test_find_by_proto_name_dahdi(self):
        dahdi_interface = 'dahdi/g1'

        trunk = TrunkFeatures()
        trunk.protocolid = 7878
        trunk.protocol = 'custom'

        usercustom = UserCustom()
        usercustom.name = 'dahdi_test'
        usercustom.id = trunk.protocolid
        usercustom.interface = dahdi_interface
        usercustom.category = 'user'

        self.add_me_all([trunk, usercustom])

        result = trunk_dao.find_by_proto_name('custom', dahdi_interface)

        self.assertEqual(result, trunk.id)

    def test_find_by_proto_name_dahdi_upper(self):
        dahdi_interface = 'dahdi/g1'

        trunk = TrunkFeatures()
        trunk.protocolid = 7878
        trunk.protocol = 'custom'

        usercustom = UserCustom()
        usercustom.name = 'dahdi_test'
        usercustom.id = trunk.protocolid
        usercustom.interface = dahdi_interface
        usercustom.category = 'user'

        self.add_me_all([trunk, usercustom])

        result = trunk_dao.find_by_proto_name('custom', 'DAHDI/g1')

        self.assertEqual(result, trunk.id)

    def test_null_input(self):
        self.assertRaises(ValueError, trunk_dao.find_by_proto_name, None, 'my_trunk')

    def test_find_by_proto_name_agent(self):
        self.assertRaises(ValueError, trunk_dao.find_by_proto_name, 'Agent', 1)
