# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from xivo_dao import directory_dao
from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctidirectoryfields import CtiDirectoryFields
from xivo_dao.alchemy.directories import Directories
from xivo_dao.alchemy.ldapserver import LdapServer
from xivo_dao.alchemy.ldapfilter import LdapFilter
from xivo_dao.tests.test_dao import DAOTestCase

from itertools import chain
from hamcrest import assert_that, contains_inanyorder, empty


class TestDirectoryLdapSources(DAOTestCase):

    def setUp(self):
        super(TestDirectoryLdapSources, self).setUp()
        ldap_server = LdapServer(
            name='myldap',
            host='myldap.example.com',
            port=636,
            securitylayer='ssl',
            protocolversion='3',
        )
        self.add_me(ldap_server)
        ldap_filter_1 = LdapFilter(
            ldapserverid=ldap_server.id,
            name='thefilter',
            user='cn=admin,dc=example,dc=com',
            passwd='53c8e7',
            basedn='dc=example,dc=com',
            attrdisplayname='cn',
            attrphonenumber='telephoneNumber',
            additionaltype='office',
        )
        self.add_me(ldap_filter_1)
        ldap_filter_2 = LdapFilter(
            ldapserverid=ldap_server.id,
            name='secondfilter',
            user='cn=admin,dc=example,dc=com',
            passwd='53c8e7',
            basedn='dc=example,dc=com',
            attrdisplayname='cn',
            attrphonenumber='telephoneNumber',
            additionaltype='office',
            filter='l=Québec',
        )
        self.add_me(ldap_filter_2)
        self.cti_directory_1 = CtiDirectories(
            name='ldapdirectory_1',
            uri='ldapfilter://{}'.format(ldap_filter_1.name),
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
        )
        self.add_me(self.cti_directory_1)
        self.cti_directory_2 = CtiDirectories(
            name='ldapdirectory_2',
            uri='ldapfilter://{}'.format(ldap_filter_2.name),
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
        )
        self.add_me(self.cti_directory_2)
        fields = {'firstname': '{givenName}',
                  'lastname': '{sn}',
                  'number': '{telephoneNumber}'}
        for name, column in fields.iteritems():
            self.add_me(CtiDirectoryFields(dir_id=self.cti_directory_1.id,
                                           fieldname=name,
                                           value=column))
            self.add_me(CtiDirectoryFields(dir_id=self.cti_directory_2.id,
                                           fieldname=name,
                                           value=column))

    def test_get_all_sources(self):
        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'ldap',
             'name': 'ldapdirectory_1',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '',
             'searched_columns': ['cn'],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
            {'type': 'ldap',
             'name': 'ldapdirectory_2',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '(l=Québec)',
             'searched_columns': ['cn'],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_that_a_missing_ldap_config_does_not_break_get_all_sources(self):
        directory_with_no_matching_config = CtiDirectories(
            name='brokenldap',
            uri='ldapfilter://missingldapconfig',
            match_direct='["cn"]',
            match_reverse='["telephoneNumber"]',
        )
        self.add_me(directory_with_no_matching_config)

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'ldap',
             'name': 'ldapdirectory_1',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '',
             'searched_columns': ['cn'],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
            {'type': 'ldap',
             'name': 'ldapdirectory_2',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '(l=Québec)',
             'searched_columns': ['cn'],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_ldap_with_no_direct_match(self):
        self.cti_directory_1.match_direct = ''

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'ldap',
             'name': 'ldapdirectory_1',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '',
             'searched_columns': [],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
            {'type': 'ldap',
             'name': 'ldapdirectory_2',
             'ldap_uri': 'ldaps://myldap.example.com:636',
             'ldap_base_dn': 'dc=example,dc=com',
             'ldap_username': 'cn=admin,dc=example,dc=com',
             'ldap_password': '53c8e7',
             'ldap_custom_filter': '(l=Québec)',
             'searched_columns': ['cn'],
             'format_columns': {
                 'firstname': '{givenName}',
                 'lastname': '{sn}',
                 'number': '{telephoneNumber}',
             }},
        ]

        assert_that(result, contains_inanyorder(*expected))


class TestDirectoryNonLdapSources(DAOTestCase):

    def setUp(self):
        super(TestDirectoryNonLdapSources, self).setUp()
        self.directory_configs = [
            {'uri': 'http://localhost:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'http://mtl.lan.example.com:9487', 'dirtype': 'xivo', 'name': 'XiVO'},
            {'uri': 'phonebook', 'dirtype': 'phonebook', 'name': 'phonebook'},
            {'uri': 'file:///tmp/test.csv', 'dirtype': 'file', 'name': 'my_csv'},
        ]
        self.cti_directory_configs = [
            {'id': 1,
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'match_direct': '["firstname", "lastname"]'},
            {'id': 2,
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'match_direct': ''},
            {'id': 3,
             'name': 'acsvfile',
             'uri': 'file:///tmp/test.csv',
             'match_direct': '["firstname", "lastname"]',
             'delimiter': '|'},
        ]
        self.cti_directory_fields_configs = [
            {'dir_id': 1,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': 1,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': 2,
             'fieldname': 'number',
             'value': '{exten}'},
            {'dir_id': 2,
             'fieldname': 'mobile',
             'value': '{mobile_phone_number}'},
            {'dir_id': 2,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
            {'dir_id': 3,
             'fieldname': 'name',
             'value': '{firstname} {lastname}'},
        ]

    def test_get_all_sources(self):
        directories = [Directories(**config) for config in self.directory_configs]
        cti_directories = [CtiDirectories(**config) for config in self.cti_directory_configs]
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(chain(directories, cti_directories, cti_directory_fields))

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'xivo',
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'delimiter': None,
             'searched_columns': [
                 'firstname',
                 'lastname',
             ],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
             }},
            {'type': 'xivo',
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'delimiter': None,
             'searched_columns': [],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
                 'name': '{firstname} {lastname}',
             }},
            {'type': 'file',
             'name': 'acsvfile',
             'uri': 'file:///tmp/test.csv',
             'delimiter': '|',
             'searched_columns': [
                 'firstname',
                 'lastname',
             ],
             'format_columns': {
                 'name': '{firstname} {lastname}',
             }},
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_get_all_sources_no_fields(self):
        directories = [Directories(**config) for config in self.directory_configs]
        cti_directories = [CtiDirectories(**config) for config in self.cti_directory_configs[:-1]]
        cti_directory_fields = [CtiDirectoryFields(**config) for config in self.cti_directory_fields_configs]
        self.add_me_all(chain(directories, cti_directories, cti_directory_fields[2:]))

        result = directory_dao.get_all_sources()

        expected = [
            {'type': 'xivo',
             'name': 'Internal',
             'uri': 'http://localhost:9487',
             'delimiter': None,
             'searched_columns': [
                 'firstname',
                 'lastname',
             ],
             'format_columns': {}},
            {'type': 'xivo',
             'name': 'mtl',
             'uri': 'http://mtl.lan.example.com:9487',
             'delimiter': None,
             'searched_columns': [],
             'format_columns': {
                 'number': '{exten}',
                 'mobile': '{mobile_phone_number}',
                 'name': '{firstname} {lastname}',
             }}
        ]

        assert_that(result, contains_inanyorder(*expected))

    def test_get_all_sources_no_directories(self):
        results = directory_dao.get_all_sources()

        assert_that(results, empty())
